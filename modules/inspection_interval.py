import streamlit as st
import math
import datetime
from modules.theme import page_header, step_badge

# ── Konstanta default ─────────────────────────────────────────────────────────
DEFAULT_JAM_KERJA   = 134.72   # jam kerja per bulan
DEFAULT_WAKTU_INS   = 4.0      # jam per inspeksi
DEFAULT_PERIODE     = 12       # bulan pengamatan

# ── Helpers kalkulasi ─────────────────────────────────────────────────────────

def hitung_parameter(jumlah_kerusakan, periode_bulan, mttr, waktu_inspeksi, jam_kerja_bulan):
    k  = jumlah_kerusakan / periode_bulan
    mu = mttr / jam_kerja_bulan
    i  = waktu_inspeksi / jam_kerja_bulan
    n_raw = math.sqrt((k * i) / mu) if mu > 0 else 0
    n  = math.ceil(n_raw)
    T  = jam_kerja_bulan / n if n > 0 else 0
    return {
        "k": k, "mu": mu, "i": i,
        "n_raw": n_raw, "n": n, "T": T,
        "jam_kerja_bulan": jam_kerja_bulan,
    }


def build_jadwal(mesin_list, tahun):
    """
    Buat dict jadwal: {nama_mesin: set of (bulan, minggu)} yang perlu inspeksi.
    Bulan 1-12, minggu 1-4.
    n = frekuensi inspeksi per bulan → tempatkan di minggu 1, (dan seterusnya jika n>1).
    """
    jadwal = {}
    for m in mesin_list:
        n = m["n"]
        slots = set()
        # distribusi minggu inspeksi dalam sebulan
        # n=1 → minggu 1; n=2 → minggu 1,3; n=3 → minggu 1,2,3; n=4 → semua
        minggu_map = {
            1: [1],
            2: [1, 3],
            3: [1, 2, 3],
            4: [1, 2, 3, 4],
        }
        minggu_ins = minggu_map.get(min(n, 4), [1])
        for bln in range(1, 13):
            for mg in minggu_ins:
                slots.add((bln, mg))
        jadwal[m["nama"]] = slots
    return jadwal


def render_kalender_html(mesin_list, jadwal, tahun):
    BULAN = ["Jan","Feb","Mar","Apr","Mei","Jun","Jul","Agt","Sep","Okt","Nov","Des"]

    # Header bulan
    header_bulan = ""
    for b in BULAN:
        header_bulan += f'<th colspan="4" style="text-align:center;padding:6px 2px;color:#f59e0b;font-size:11px;border-bottom:1px solid #1e2a45;border-right:1px solid #1e2a45;">{b}</th>'

    # Header minggu
    header_minggu = ""
    for _ in BULAN:
        for w in range(1, 5):
            header_minggu += f'<th style="text-align:center;padding:4px 1px;color:#64748b;font-size:10px;border-bottom:1px solid #1e2a45;">{w}</th>'

    # Baris mesin
    rows = ""
    for m in mesin_list:
        nama  = m["nama"]
        slots = jadwal.get(nama, set())
        row   = f'<td style="padding:6px 10px;color:#f8fafc;font-size:11px;font-family:IBM Plex Mono,monospace;white-space:nowrap;border-right:2px solid #1e2a45;position:sticky;left:0;background:#0a0e1a;z-index:1;">{nama}</td>'
        for bln in range(1, 13):
            for mg in range(1, 5):
                if (bln, mg) in slots:
                    cell = '<td style="text-align:center;padding:3px 1px;"><span style="color:#22c55e;font-weight:700;font-size:12px;">I</span></td>'
                else:
                    cell = '<td style="text-align:center;padding:3px 1px;color:#1e2a45;font-size:10px;">·</td>'
                row += cell
        rows += f'<tr style="border-bottom:1px solid #0f1628;">{row}</tr>'

    html = f"""
    <div style="overflow-x:auto;margin-top:8px;">
      <table style="border-collapse:collapse;background:#0a0e1a;font-family:IBM Plex Mono,monospace;min-width:900px;width:100%;">
        <thead>
          <tr>
            <th style="padding:6px 10px;color:#94a3b8;font-size:11px;text-align:left;
                       border-bottom:1px solid #1e2a45;border-right:2px solid #1e2a45;
                       position:sticky;left:0;background:#0a0e1a;z-index:2;">
              Mesin / Minggu Ke-
            </th>
            {header_bulan}
          </tr>
          <tr>
            <th style="border-right:2px solid #1e2a45;position:sticky;left:0;background:#0a0e1a;z-index:2;"></th>
            {header_minggu}
          </tr>
        </thead>
        <tbody>
          {rows}
        </tbody>
      </table>
    </div>
    <p style="color:#475569;font-family:IBM Plex Mono,monospace;font-size:10px;margin-top:8px;">
      <span style="color:#22c55e;font-weight:700;">I</span> = Jadwal Inspeksi 
    </p>
    """
    return html


# ── Main show() ───────────────────────────────────────────────────────────────

def show():
    page_header("🗓️", "Rencana Inspeksi", "Frekuensi inspeksi optimal & kalender tahunan")

    tahun = datetime.datetime.now().year

    # ── Ambil data mesin dari database ────────────────────────────────────────
    try:
        from modules import database
        conn  = database.get_connection()
        cur   = conn.cursor()
        cur.execute("SELECT DISTINCT nama_mesin FROM kerusakan ORDER BY nama_mesin")
        mesin_db = [r[0] for r in cur.fetchall()]

        # Hitung MTTR per mesin dari DB
        mttr_db = {}
        for nm in mesin_db:
            cur.execute("""
                SELECT AVG(ttr) FROM kerusakan
                WHERE nama_mesin = ? AND ttr IS NOT NULL AND ttr > 0
            """, (nm,))
            row = cur.fetchone()
            mttr_db[nm] = round(row[0], 4) if row and row[0] else 0.0

        # Hitung jumlah kerusakan per mesin
        keru_db = {}
        for nm in mesin_db:
            cur.execute("SELECT COUNT(*) FROM kerusakan WHERE nama_mesin = ?", (nm,))
            keru_db[nm] = cur.fetchone()[0]

        conn.close()
        db_ok = True
    except Exception as e:
        mesin_db  = []
        mttr_db   = {}
        keru_db   = {}
        db_ok     = False
        st.warning(f"⚠️ Tidak dapat membaca database: {e}")

    # ── Step 1: Parameter Global ──────────────────────────────────────────────
    step_badge(1, "Parameter Global")

    col1, col2, col3 = st.columns(3)
    with col1:
        jam_kerja = st.number_input("Jam kerja per bulan", value=DEFAULT_JAM_KERJA, min_value=1.0, format="%.2f")
    with col2:
        waktu_ins = st.number_input("Waktu inspeksi (jam)", value=DEFAULT_WAKTU_INS, min_value=0.1, format="%.2f")
    with col3:
        periode   = st.number_input("Periode pengamatan (bulan)", value=DEFAULT_PERIODE, min_value=1, step=1)

    st.markdown("<hr style='border-color:#1e2a45;margin:16px 0'>", unsafe_allow_html=True)

    # ── Step 2: Data Mesin ────────────────────────────────────────────────────
    step_badge(2, "Data Mesin & Parameter")

    # Inisialisasi session state untuk tabel mesin
    if "ins_mesin_rows" not in st.session_state:
        if db_ok and mesin_db:
            st.session_state.ins_mesin_rows = [
                {
                    "nama"             : nm,
                    "jumlah_kerusakan" : keru_db.get(nm, 0),
                    "mttr"             : mttr_db.get(nm, 0.0),
                }
                for nm in mesin_db
            ]
        else:
            st.session_state.ins_mesin_rows = [
                {"nama": "Mesin A", "jumlah_kerusakan": 8, "mttr": 20.53}
            ]

    rows = st.session_state.ins_mesin_rows

    # Label kolom
    c1, c2, c3 = st.columns([3, 2, 2])
    c1.markdown("<p style='color:#475569;font-size:10px;font-family:IBM Plex Mono,monospace;margin-bottom:4px;'>NAMA MESIN</p>", unsafe_allow_html=True)
    c2.markdown("<p style='color:#475569;font-size:10px;font-family:IBM Plex Mono,monospace;margin-bottom:4px;'>JML KERUSAKAN</p>", unsafe_allow_html=True)
    c3.markdown("<p style='color:#475569;font-size:10px;font-family:IBM Plex Mono,monospace;margin-bottom:4px;'>MTTR (jam)</p>", unsafe_allow_html=True)

    # Render editor baris per mesin (nama read-only, jumlah & MTTR bisa diedit)
    for idx, row in enumerate(rows):
        c1, c2, c3 = st.columns([3, 2, 2])
        with c1:
            st.markdown(f"<p style='color:#f8fafc;font-family:IBM Plex Mono,monospace;font-size:13px;padding:8px 4px;'>{row['nama']}</p>", unsafe_allow_html=True)
        with c2:
            row["jumlah_kerusakan"] = st.number_input(
                "k", value=int(row["jumlah_kerusakan"]),
                min_value=1, key=f"ins_k_{idx}",
                label_visibility="collapsed"
            )
        with c3:
            row["mttr"] = st.number_input(
                "mttr", value=float(row["mttr"]),
                min_value=0.01, format="%.2f",
                key=f"ins_mttr_{idx}",
                label_visibility="collapsed"
            )

    st.markdown("<hr style='border-color:#1e2a45;margin:16px 0'>", unsafe_allow_html=True)

    # ── Step 3: Hitung & Tampilkan Hasil ─────────────────────────────────────
    step_badge(3, "Hasil Perhitungan")

    if st.button("⚙️ Hitung Frekuensi Inspeksi", type="primary"):
        valid_rows = [r for r in rows if r["nama"].strip() and r["mttr"] > 0]
        if not valid_rows:
            st.error("Isi minimal satu mesin dengan nama dan MTTR yang valid.")
            return

        hasil = []
        for r in valid_rows:
            p = hitung_parameter(
                jumlah_kerusakan  = r["jumlah_kerusakan"],
                periode_bulan     = periode,
                mttr              = r["mttr"],
                waktu_inspeksi    = waktu_ins,
                jam_kerja_bulan   = jam_kerja,
            )
            p["nama"] = r["nama"]
            hasil.append(p)

        st.session_state["ins_hasil"] = hasil

    if "ins_hasil" not in st.session_state:
        st.info("Tekan tombol **Hitung** untuk melihat hasil.")
        return

    hasil = st.session_state["ins_hasil"]

    # Tabel hasil perhitungan
    header_css = "color:#f59e0b;font-size:10px;font-family:IBM Plex Mono,monospace;letter-spacing:1px;padding:6px 8px;border-bottom:1px solid #1e2a45;text-align:center;"
    cell_css   = "color:#f8fafc;font-size:12px;font-family:IBM Plex Mono,monospace;padding:6px 8px;text-align:center;border-bottom:1px solid #0f1628;"
    name_css   = "color:#f8fafc;font-size:12px;font-family:IBM Plex Mono,monospace;padding:6px 8px;text-align:left;border-bottom:1px solid #0f1628;"

    tabel_rows = ""
    for h in hasil:
        tabel_rows += f"""
        <tr>
          <td style="{name_css}">{h['nama']}</td>
          <td style="{cell_css}">{h['k']:.4f}</td>
          <td style="{cell_css}">{h['mu']:.4f}</td>
          <td style="{cell_css}">{h['i']:.4f}</td>
          <td style="{cell_css}">{h['n_raw']:.4f}</td>
          <td style="{cell_css};color:#22c55e;font-weight:700;">{h['n']}</td>
          <td style="{cell_css};color:#38bdf8;">{h['T']:.2f} jam</td>
        </tr>
        """

    st.markdown(f"""
    <div style="overflow-x:auto;margin-bottom:20px;">
      <table style="border-collapse:collapse;background:#0a0e1a;width:100%;font-family:IBM Plex Mono,monospace;">
        <thead>
          <tr>
            <th style="{header_css};text-align:left;">Mesin</th>
            <th style="{header_css};">k (per bulan)</th>
            <th style="{header_css};">μ (bulan)</th>
            <th style="{header_css};">i (bulan)</th>
            <th style="{header_css};">n raw</th>
            <th style="{header_css};color:#22c55e;">n (roundup)</th>
            <th style="{header_css};color:#38bdf8;">T interval</th>
          </tr>
        </thead>
        <tbody>{tabel_rows}</tbody>
      </table>
    </div>
    """, unsafe_allow_html=True)

    # Detail rumus per mesin (expander)
    for h in hasil:
        with st.expander(f"📐 Detail perhitungan — {h['nama']}"):
            st.markdown(f"""
            <div style="font-family:IBM Plex Mono,monospace;font-size:12px;line-height:2;">
              <span style="color:#64748b;">k  = {int(sum(r['jumlah_kerusakan'] for r in rows if r['nama']==h['nama']))} / {periode}</span>
                 = <span style="color:#f8fafc;">{h['k']:.4f} per bulan</span><br>
              <span style="color:#64748b;">μ  = MTTR / jam kerja</span>
                 = <span style="color:#f8fafc;">{h['mu']:.4f} bulan</span><br>
              <span style="color:#64748b;">i  = {waktu_ins} / {jam_kerja}</span>
                 = <span style="color:#f8fafc;">{h['i']:.4f} bulan</span><br>
              <span style="color:#64748b;">n  = √((k × i) / μ)</span>
                 = √(({h['k']:.4f} × {h['i']:.4f}) / {h['mu']:.4f})
                 = √({(h['k']*h['i']/h['mu']):.4f})
                 = <span style="color:#f59e0b;">{h['n_raw']:.4f}</span>
                 → ROUNDUP = <span style="color:#22c55e;font-weight:700;">{h['n']}</span><br>
              <span style="color:#64748b;">T  = {jam_kerja} / {h['n']}</span>
                 = <span style="color:#38bdf8;">{h['T']:.2f} jam</span>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#1e2a45;margin:20px 0'>", unsafe_allow_html=True)

    # ── Step 4: Kalender Inspeksi ─────────────────────────────────────────────
    step_badge(4, "Kalender Inspeksi")

    jadwal  = build_jadwal(hasil, tahun)
    kal_html = render_kalender_html(hasil, jadwal, tahun)
    st.markdown(kal_html, unsafe_allow_html=True)