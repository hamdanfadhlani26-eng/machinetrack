import streamlit as st
import math
import datetime
from modules.theme import page_header, step_badge
from modules import database

# ── Konstanta default ─────────────────────────────────────────────────────────
DEFAULT_JAM_KERJA   = 134.72
DEFAULT_WAKTU_INS   = 4.0
DEFAULT_PERIODE     = 12


# ── Helpers kalkulasi ─────────────────────────────────────────────────────────

def hitung_parameter(jumlah_kerusakan, periode_bulan, mttr, waktu_inspeksi, jam_kerja_bulan):
    k       = jumlah_kerusakan / periode_bulan
    mu      = mttr / jam_kerja_bulan
    i       = waktu_inspeksi / jam_kerja_bulan
    n_raw   = math.sqrt((k * i) / mu) if mu > 0 else 0
    n       = math.ceil(n_raw)
    T       = jam_kerja_bulan / n if n > 0 else 0
    return {"k": k, "mu": mu, "i": i, "n_raw": n_raw, "n": n, "T": T,
            "jam_kerja_bulan": jam_kerja_bulan}


def build_minggu_slots(n: int, minggu_awal: int) -> list[int]:
    """
    Bangun daftar minggu inspeksi dalam sebulan.
    Inspeksi pertama di minggu_awal, berikutnya dengan jarak seragam.

    Contoh:
      n=1, minggu_awal=3 → [3]
      n=2, minggu_awal=1 → [1, 3]  (jarak 2)
      n=2, minggu_awal=2 → [2, 4]  (jarak 2)
      n=3, minggu_awal=1 → [1, 2, 3]
      n=4              → [1, 2, 3, 4]
    """
    n = min(n, 4)
    if n == 1:
        return [minggu_awal]
    if n == 4:
        return [1, 2, 3, 4]

    # Jarak antar inspeksi = floor(4 / n)
    jarak = 4 // n
    slots = []
    mg = minggu_awal
    for _ in range(n):
        slots.append(mg)
        mg += jarak
    # Pastikan semua dalam rentang 1–4, wrap jika perlu
    slots = [((s - 1) % 4) + 1 for s in slots]
    # Hilangkan duplikat sambil pertahankan urutan
    seen = set()
    unique = []
    for s in slots:
        if s not in seen:
            seen.add(s)
            unique.append(s)
    # Jika kurang dari n (karena wrap), tambahkan dari yang tersedia
    available = [w for w in [1, 2, 3, 4] if w not in seen]
    while len(unique) < n and available:
        unique.append(available.pop(0))
    return sorted(unique)


def build_jadwal(mesin_list):
    jadwal = {}
    for m in mesin_list:
        n           = m["n"]
        minggu_awal = m.get("minggu_awal", 1)
        slots       = set()
        minggu_ins  = build_minggu_slots(n, minggu_awal)
        for bln in range(1, 13):
            for mg in minggu_ins:
                slots.add((bln, mg))
        jadwal[m["nama"]] = slots
    return jadwal


def render_kalender_html(mesin_list, jadwal):
    BULAN = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agt","Sep","Okt","Nov","Des"]
    header_bulan = ""
    for b in BULAN:
        header_bulan += (
            f'<th colspan="4" style="text-align:center;padding:6px 2px;color:#b45309;'
            f'font-size:11px;border-bottom:1px solid #d6cfc4;border-right:1px solid #d6cfc4;">{b}</th>'
        )
    header_minggu = ""
    for _ in BULAN:
        for w in range(1, 5):
            header_minggu += (
                f'<th style="text-align:center;padding:4px 1px;color:#78716c;'
                f'font-size:10px;border-bottom:1px solid #d6cfc4;">{w}</th>'
            )
    rows = ""
    for m in mesin_list:
        nama  = m["nama"]
        slots = jadwal.get(nama, set())
        row   = (
            f'<td style="padding:6px 10px;color:#1c1917;font-size:11px;'
            f'font-family:IBM Plex Mono,monospace;white-space:nowrap;'
            f'border-right:2px solid #d6cfc4;position:sticky;left:0;'
            f'background:#faf8f5;z-index:1;">{nama}</td>'
        )
        for bln in range(1, 13):
            for mg in range(1, 5):
                if (bln, mg) in slots:
                    cell = '<td style="text-align:center;padding:3px 1px;"><span style="color:#16a34a;font-weight:700;font-size:12px;">I</span></td>'
                else:
                    cell = '<td style="text-align:center;padding:3px 1px;color:#d6cfc4;font-size:10px;">·</td>'
                row += cell
        rows += f'<tr style="border-bottom:1px solid #ede8e0;">{row}</tr>'

    return f"""
    <div style="overflow-x:auto;margin-top:8px;">
      <table style="border-collapse:collapse;background:#faf8f5;font-family:IBM Plex Mono,monospace;min-width:900px;width:100%;">
        <thead>
          <tr>
            <th style="padding:6px 10px;color:#57534e;font-size:11px;text-align:left;
                       border-bottom:1px solid #d6cfc4;border-right:2px solid #d6cfc4;
                       position:sticky;left:0;background:#faf8f5;z-index:2;">
              Mesin / Minggu Ke-
            </th>
            {header_bulan}
          </tr>
          <tr>
            <th style="border-right:2px solid #d6cfc4;position:sticky;left:0;background:#faf8f5;z-index:2;"></th>
            {header_minggu}
          </tr>
        </thead>
        <tbody>
          {rows}
        </tbody>
      </table>
    </div>
    <p style="color:#78716c;font-family:IBM Plex Mono,monospace;font-size:10px;margin-top:8px;">
      <span style="color:#16a34a;font-weight:700;">I</span> = Jadwal Inspeksi
    </p>
    """


# ── Main show() ───────────────────────────────────────────────────────────────

def show():
    page_header("🗓️", "Rencana Inspeksi", "Frekuensi inspeksi optimal & kalender tahunan")

    tahun_skrg = datetime.datetime.now().year

    # ── Ambil data mesin dari database ────────────────────────────────────────
    try:
        mesin_db = database.get_machine_names()
        mttr_db  = {}
        keru_db  = {}
        for nm in mesin_db:
            ttrs = database.get_ttr_by_machine(nm)
            mttr_db[nm] = round(sum(ttrs) / len(ttrs), 4) if ttrs else 0.0
            with database.get_conn() as conn:
                row = conn.execute(
                    "SELECT COUNT(*) as cnt FROM failure_data WHERE mesin=?", (nm,)
                ).fetchone()
                keru_db[nm] = row["cnt"] if row else 0
        db_ok = True
    except Exception as e:
        mesin_db = []
        mttr_db  = {}
        keru_db  = {}
        db_ok    = False
        st.warning(f"⚠️ Tidak dapat membaca database: {e}")

    # ── Step 1: Pilih Tahun & Parameter Global ────────────────────────────────
    step_badge(1, "Tahun & Parameter Global")

    col_thn, col1, col2, col3 = st.columns(4)
    with col_thn:
        tahun_options = list(range(tahun_skrg + 1, tahun_skrg + 6))
        tahun = st.selectbox(
            "Tahun Rencana",
            options=tahun_options,
            index=0,
        )
    with col1:
        jam_kerja = st.number_input("Jam operasi mesin per bulan", value=DEFAULT_JAM_KERJA,
                                     min_value=1.0, format="%.2f")
    with col2:
        waktu_ins = st.number_input("Durasi 1 kali inspeksi (jam)", value=DEFAULT_WAKTU_INS,
                                     min_value=0.1, format="%.2f")
    with col3:
        periode = st.number_input("Periode data historis (bulan)", value=DEFAULT_PERIODE,
                                   min_value=1, step=1)

    st.markdown("<hr style='border-color:#e7e0d6;margin:16px 0'>", unsafe_allow_html=True)

    # ── Step 2: Pilih & Edit Data Mesin ──────────────────────────────────────
    step_badge(2, "Pilih Mesin & Parameter")

    if db_ok and mesin_db:
        mesin_dipilih = st.multiselect(
            "Pilih mesin yang akan direncanakan",
            options=mesin_db,
            default=mesin_db[:1] if mesin_db else [],
        )
    else:
        mesin_dipilih = []
        st.info("Tidak ada mesin di database. Tambahkan mesin di menu Data Kerusakan.")

    if not mesin_dipilih:
        st.info("Pilih minimal satu mesin untuk melanjutkan.")
        return

    if "ins_mesin_rows" not in st.session_state:
        st.session_state.ins_mesin_rows = {}

    for nm in mesin_dipilih:
        if nm not in st.session_state.ins_mesin_rows:
            st.session_state.ins_mesin_rows[nm] = {
                "nama"             : nm,
                "jumlah_kerusakan" : keru_db.get(nm, 0),
                "mttr"             : mttr_db.get(nm, 0.0),
            }

    rows = [st.session_state.ins_mesin_rows[nm] for nm in mesin_dipilih]

    c1, c2, c3 = st.columns([3, 2, 2])
    c1.markdown("<p style='color:#78716c;font-size:10px;font-family:IBM Plex Mono,monospace;margin-bottom:4px;'>NAMA MESIN</p>", unsafe_allow_html=True)
    c2.markdown("<p style='color:#78716c;font-size:10px;font-family:IBM Plex Mono,monospace;margin-bottom:4px;'>JML KERUSAKAN</p>", unsafe_allow_html=True)
    c3.markdown("<p style='color:#78716c;font-size:10px;font-family:IBM Plex Mono,monospace;margin-bottom:4px;'>MTTR (jam)</p>", unsafe_allow_html=True)

    for idx, row in enumerate(rows):
        c1, c2, c3 = st.columns([3, 2, 2])
        with c1:
            st.markdown(
                f"<p style='color:#1c1917;font-family:IBM Plex Mono,monospace;"
                f"font-size:13px;padding:8px 4px;font-weight:600;'>{row['nama']}</p>",
                unsafe_allow_html=True,
            )
        with c2:
            row["jumlah_kerusakan"] = st.number_input(
                "k", value=int(row["jumlah_kerusakan"]),
                min_value=1, key=f"ins_k_{row['nama']}",
                label_visibility="collapsed"
            )
        with c3:
            row["mttr"] = st.number_input(
                "mttr", value=float(row["mttr"]),
                min_value=0.01, format="%.2f",
                key=f"ins_mttr_{row['nama']}",
                label_visibility="collapsed"
            )

    st.markdown("<hr style='border-color:#e7e0d6;margin:16px 0'>", unsafe_allow_html=True)

    # ── Step 3: Hitung ────────────────────────────────────────────────────────
    step_badge(3, "Hasil Perhitungan")

    if st.button("⚙️ Hitung Frekuensi Inspeksi", type="primary"):
        valid_rows = [r for r in rows if r["nama"].strip() and r["mttr"] > 0]
        if not valid_rows:
            st.error("Isi minimal satu mesin dengan MTTR yang valid.")
            return
        hasil = []
        for r in valid_rows:
            p = hitung_parameter(
                jumlah_kerusakan = r["jumlah_kerusakan"],
                periode_bulan    = periode,
                mttr             = r["mttr"],
                waktu_inspeksi   = waktu_ins,
                jam_kerja_bulan  = jam_kerja,
            )
            p["nama"]      = r["nama"]
            p["jam_kerja"] = jam_kerja
            p["waktu_ins"] = waktu_ins
            p["periode"]   = periode
            hasil.append(p)
        st.session_state["ins_hasil"]     = hasil
        st.session_state["ins_tahun"]     = tahun
        st.session_state["ins_tersimpan"] = False

    if "ins_hasil" not in st.session_state:
        st.info("Tekan tombol **Hitung** untuk melihat hasil.")
        return

    hasil       = st.session_state["ins_hasil"]
    tahun_hasil = st.session_state.get("ins_tahun", tahun)

    header_css = "color:#b45309;font-size:10px;font-family:IBM Plex Mono,monospace;letter-spacing:1px;padding:6px 8px;border-bottom:1px solid #d6cfc4;text-align:center;background:#fef3c7;"
    cell_css   = "color:#1c1917;font-size:12px;font-family:IBM Plex Mono,monospace;padding:6px 8px;text-align:center;border-bottom:1px solid #ede8e0;"
    name_css   = "color:#1c1917;font-size:12px;font-family:IBM Plex Mono,monospace;padding:6px 8px;text-align:left;border-bottom:1px solid #ede8e0;font-weight:600;"

    tabel_rows = ""
    for h in hasil:
        tabel_rows += f"""
        <tr>
          <td style="{name_css}">{h['nama']}</td>
          <td style="{cell_css}">{h['k']:.4f}</td>
          <td style="{cell_css}">{h['mu']:.4f}</td>
          <td style="{cell_css}">{h['i']:.4f}</td>
          <td style="{cell_css}">{h['n_raw']:.4f}</td>
          <td style="{cell_css};color:#16a34a;font-weight:700;">{h['n']}</td>
          <td style="{cell_css};color:#b45309;font-weight:600;">{h['T']:.2f} jam</td>
        </tr>
        """

    st.html(f"""
    <div style="overflow-x:auto;margin-bottom:20px;">
      <table style="border-collapse:collapse;background:#faf8f5;width:100%;font-family:IBM Plex Mono,monospace;">
        <thead>
          <tr>
            <th style="{header_css};text-align:left;">Mesin</th>
            <th style="{header_css};">k (per bulan)</th>
            <th style="{header_css};">μ (bulan)</th>
            <th style="{header_css};">i (bulan)</th>
            <th style="{header_css};">n raw</th>
            <th style="{header_css};color:#16a34a;">n (roundup)</th>
            <th style="{header_css};color:#b45309;">T interval</th>
          </tr>
        </thead>
        <tbody>{tabel_rows}</tbody>
      </table>
    </div>
    """)

    for h in hasil:
        with st.expander(f"📐 Detail perhitungan — {h['nama']}"):
            st.html(f"""
            <div style="font-family:IBM Plex Mono,monospace;font-size:12px;line-height:2;background:#fef9f0;padding:16px;border-radius:8px;">
              <span style="color:#78716c;">k  = jumlah kerusakan / periode</span>
                 = <span style="color:#1c1917;font-weight:600;">{h['k']:.4f} per bulan</span><br>
              <span style="color:#78716c;">μ  = MTTR / jam kerja</span>
                 = <span style="color:#1c1917;font-weight:600;">{h['mu']:.4f} bulan</span><br>
              <span style="color:#78716c;">i  = {waktu_ins} / {jam_kerja}</span>
                 = <span style="color:#1c1917;font-weight:600;">{h['i']:.4f} bulan</span><br>
              <span style="color:#78716c;">n  = √((k × i) / μ)</span>
                 = √(({h['k']:.4f} × {h['i']:.4f}) / {h['mu']:.4f})
                 = <span style="color:#b45309;font-weight:700;">{h['n_raw']:.4f}</span>
                 → ROUNDUP = <span style="color:#16a34a;font-weight:700;">{h['n']}</span><br>
              <span style="color:#78716c;">T  = {jam_kerja} / {h['n']}</span>
                 = <span style="color:#b45309;font-weight:700;">{h['T']:.2f} jam</span>
            </div>
            """)

    st.markdown("<hr style='border-color:#e7e0d6;margin:20px 0'>", unsafe_allow_html=True)

    # ── Step 4: Pilih Minggu Awal per Mesin ──────────────────────────────────
    step_badge(4, "Tentukan Minggu Mulai Inspeksi")

    st.markdown(
        "<p style='color:#57534e;font-size:12px;font-family:IBM Plex Mono,monospace;margin-bottom:12px;'>"
        "Tentukan minggu pertama pelaksanaan inspeksi untuk setiap mesin. "
        "Inspeksi berikutnya akan mengikuti pola yang konsisten berdasarkan minggu awal ini.</p>",
        unsafe_allow_html=True,
    )

    if "ins_minggu_awal" not in st.session_state:
        st.session_state["ins_minggu_awal"] = {}

    for h in hasil:
        nama = h["nama"]
        n    = min(h["n"], 4)

        # Tentukan pilihan minggu awal yang valid berdasarkan n
        # Minggu awal harus memungkinkan n inspeksi dalam 4 minggu tanpa keluar batas
        if n == 1:
            pilihan_awal = [1, 2, 3, 4]
        elif n == 2:
            pilihan_awal = [1, 2]   # awal 1→[1,3], awal 2→[2,4]
        elif n == 3:
            pilihan_awal = [1, 2]   # awal 1→[1,2,3], awal 2→[2,3,4]
        else:
            pilihan_awal = [1]      # n=4 selalu semua minggu

        default_idx = 0
        if nama in st.session_state["ins_minggu_awal"]:
            prev = st.session_state["ins_minggu_awal"][nama]
            if prev in pilihan_awal:
                default_idx = pilihan_awal.index(prev)

        col_nama, col_pilih, col_preview = st.columns([3, 2, 4])

        with col_nama:
            st.markdown(
                f"<p style='color:#1c1917;font-family:IBM Plex Mono,monospace;"
                f"font-size:13px;padding:8px 4px;font-weight:600;'>{nama}</p>",
                unsafe_allow_html=True,
            )

        with col_pilih:
            mg_awal = st.selectbox(
                "Minggu awal",
                options=pilihan_awal,
                index=default_idx,
                format_func=lambda x: f"Minggu {x}",
                key=f"ins_mw_{nama}",
                label_visibility="collapsed",
            )
            st.session_state["ins_minggu_awal"][nama] = mg_awal

        with col_preview:
            slots_preview = build_minggu_slots(n, mg_awal)
            slots_str = " · ".join([f"Minggu {s}" for s in slots_preview])
            st.markdown(
                f"<p style='color:#16a34a;font-family:IBM Plex Mono,monospace;"
                f"font-size:11px;padding:8px 4px;'>"
                f"→ Inspeksi tiap bulan pada: <strong>{slots_str}</strong></p>",
                unsafe_allow_html=True,
            )

    # Tempelkan minggu_awal ke setiap hasil
    for h in hasil:
        h["minggu_awal"] = st.session_state["ins_minggu_awal"].get(h["nama"], 1)

    st.markdown("<hr style='border-color:#e7e0d6;margin:20px 0'>", unsafe_allow_html=True)

    # ── Step 5: Kalender Preview ──────────────────────────────────────────────
    step_badge(5, f"Preview Kalender Inspeksi {tahun_hasil}")

    jadwal   = build_jadwal(hasil)
    kal_html = render_kalender_html(hasil, jadwal)
    st.html(kal_html)

    st.markdown("<hr style='border-color:#e7e0d6;margin:20px 0'>", unsafe_allow_html=True)

    # ── Step 6: Simpan Rencana ────────────────────────────────────────────────
    step_badge(6, "Simpan Rencana Inspeksi")

    sudah_tersimpan = st.session_state.get("ins_tersimpan", False)

    if sudah_tersimpan:
        st.success("✅ Rencana inspeksi berhasil disimpan ke database!")
        if st.button("💾 Simpan Versi Baru"):
            st.session_state["ins_tersimpan"] = False
            st.rerun()
    else:
        st.markdown(
            f"<p style='color:#57534e;font-size:12px;font-family:IBM Plex Mono,monospace;'>"
            f"Klik tombol di bawah untuk menyimpan rencana inspeksi tahun "
            f"<strong style='color:#b45309;'>{tahun_hasil}</strong> "
            f"ke database.</p>",
            unsafe_allow_html=True,
        )
        if st.button("💾 Simpan Rencana Inspeksi", type="primary"):
            try:
                for h in hasil:
                    nama       = h["nama"]
                    n          = min(h["n"], 4)
                    mg_awal    = h.get("minggu_awal", 1)
                    minggu_ins = build_minggu_slots(n, mg_awal)
                    slots      = []
                    for bln in range(1, 13):
                        for mg in minggu_ins:
                            slots.append((bln, mg))
                    database.simpan_rencana_inspeksi(
                        mesin        = nama,
                        tahun        = tahun_hasil,
                        n            = h["n"],
                        jam_kerja    = h["jam_kerja"],
                        waktu_ins    = h["waktu_ins"],
                        periode      = h["periode"],
                        jadwal_slots = slots,
                    )
                st.session_state["ins_tersimpan"] = True
                st.rerun()
            except Exception as e:
                st.error(f"❌ Gagal menyimpan: {e}")