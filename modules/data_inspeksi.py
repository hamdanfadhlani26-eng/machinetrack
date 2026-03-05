import streamlit as st
import datetime
from modules.theme import page_header, step_badge

# ── Helpers ───────────────────────────────────────────────────────────────────

BULAN_NAMA = ["Januari","Februari","Maret","April","Mei","Juni",
               "Juli","Agustus","September","Oktober","November","Desember"]

MINGGU_MAP = {
    1: [1],
    2: [1, 3],
    3: [1, 2, 3],
    4: [1, 2, 3, 4],
}

def get_minggu_dari_tanggal(tanggal: datetime.date) -> int:
    """Konversi tanggal ke minggu dalam bulan (1-4)."""
    d = tanggal.day
    if d <= 7:   return 1
    if d <= 14:  return 2
    if d <= 21:  return 3
    return 4

def get_minggu_sekarang() -> tuple:
    """Return (bulan, minggu) saat ini."""
    today = datetime.date.today()
    return today.month, get_minggu_dari_tanggal(today)

def sudah_lewat(bulan_rencana: int, minggu_rencana: int) -> bool:
    """Cek apakah minggu rencana sudah lewat dari sekarang."""
    bln_skrg, mgg_skrg = get_minggu_sekarang()
    if bulan_rencana < bln_skrg:
        return True
    if bulan_rencana == bln_skrg and minggu_rencana < mgg_skrg:
        return True
    return False

def hitung_status(bulan_rencana, minggu_rencana, bulan_aktual, minggu_aktual):
    """Hitung status inspeksi berdasarkan rencana vs aktual."""
    if bulan_rencana == bulan_aktual and minggu_rencana == minggu_aktual:
        return "✅ Tepat"
    # Konversi ke angka minggu global untuk perbandingan
    rencana_global = (bulan_rencana - 1) * 4 + minggu_rencana
    aktual_global  = (bulan_aktual  - 1) * 4 + minggu_aktual
    if aktual_global > rencana_global:
        return "⚠️ Terlambat"
    return "⚡ Lebih Cepat"

def status_color(status: str) -> str:
    if "Tepat"       in status: return "#22c55e"
    if "Terlambat"   in status: return "#f59e0b"
    if "Lebih Cepat" in status: return "#38bdf8"
    if "Tidak"       in status: return "#ef4444"
    return "#64748b"  # Belum

# ── Main show() ───────────────────────────────────────────────────────────────

def show():
    page_header("📝", "Data Inspeksi", "Evaluasi realisasi vs rencana inspeksi")

    # ── Guard: cek apakah Modul 5 sudah dijalankan ───────────────────────────
    if "ins_hasil" not in st.session_state or not st.session_state["ins_hasil"]:
        st.markdown("""
        <div style="background:#1e2a45;border:1px solid #f59e0b;border-radius:10px;
                    padding:24px;text-align:center;margin-top:32px;">
            <p style="color:#f59e0b;font-size:18px;font-family:IBM Plex Mono,monospace;
                      font-weight:700;margin-bottom:8px;">⚠️ Data Rencana Belum Tersedia</p>
            <p style="color:#94a3b8;font-size:13px;font-family:IBM Plex Sans,sans-serif;margin:0;">
                Silakan lakukan perhitungan terlebih dahulu di menu
                <strong style="color:#f8fafc;">🗓️ Rencana Inspeksi</strong>
                untuk menghasilkan jadwal rencana inspeksi.
            </p>
        </div>
        """, unsafe_allow_html=True)
        return

    hasil    = st.session_state["ins_hasil"]
    tahun    = datetime.date.today().year
    bln_skrg, mgg_skrg = get_minggu_sekarang()

    # ── Bangun semua slot rencana ─────────────────────────────────────────────
    # Format key session state: "real_{nama}_{bulan}_{minggu}"
    semua_slot = []
    for h in hasil:
        nama = h["nama"]
        n    = min(h["n"], 4)
        minggu_ins = MINGGU_MAP.get(n, [1])
        for bln in range(1, 13):
            for mg in minggu_ins:
                semua_slot.append({
                    "nama"           : nama,
                    "bulan_rencana"  : bln,
                    "minggu_rencana" : mg,
                })

    # ── Step 1: Input Realisasi ───────────────────────────────────────────────
    step_badge(1, "Input Realisasi Inspeksi")

    st.markdown(
        "<p style='color:#94a3b8;font-size:12px;font-family:IBM Plex Mono,monospace;"
        "margin-bottom:16px;'>Isi tanggal atau pilih minggu realisasi untuk setiap jadwal "
        "inspeksi. Jadwal yang sudah lewat tanpa realisasi akan otomatis ditandai "
        "<span style=\"color:#ef4444;\">Tidak Terlaksana</span>.</p>",
        unsafe_allow_html=True,
    )

    # Filter: tampilkan per mesin dengan expander
    for h in hasil:
        nama      = h["nama"]
        n         = min(h["n"], 4)
        minggu_ins = MINGGU_MAP.get(n, [1])
        slot_mesin = [s for s in semua_slot if s["nama"] == nama]

        with st.expander(f"🔧 {nama}  —  {n}x inspeksi/bulan  ({len(slot_mesin)} jadwal/tahun)", expanded=True):
            for slot in slot_mesin:
                bln = slot["bulan_rencana"]
                mg  = slot["minggu_rencana"]
                key_mode   = f"mode_{nama}_{bln}_{mg}"
                key_date   = f"date_{nama}_{bln}_{mg}"
                key_bln_ak = f"bln_{nama}_{bln}_{mg}"
                key_mgg_ak = f"mgg_{nama}_{bln}_{mg}"

                sudah_lewat_flag = sudah_lewat(bln, mg)

                # Label rencana
                label_rencana = f"{BULAN_NAMA[bln-1]} Minggu {mg}"

                col_rencana, col_mode, col_input, col_status_preview = st.columns([2, 2, 3, 2])

                with col_rencana:
                    st.markdown(
                        f"<p style='color:#f59e0b;font-family:IBM Plex Mono,monospace;"
                        f"font-size:12px;padding-top:8px;'>📅 {label_rencana}</p>",
                        unsafe_allow_html=True,
                    )

                with col_mode:
                    mode = st.selectbox(
                        "Input",
                        options=["Pilih Minggu", "Pilih Tanggal"],
                        key=key_mode,
                        label_visibility="collapsed",
                    )

                with col_input:
                    if mode == "Pilih Tanggal":
                        # Default tanggal = hari pertama minggu rencana
                        hari_default = (mg - 1) * 7 + 1
                        try:
                            default_date = datetime.date(tahun, bln, hari_default)
                        except:
                            default_date = datetime.date(tahun, bln, 1)

                        tgl = st.date_input(
                            "Tanggal realisasi",
                            value=st.session_state.get(key_date, None),
                            min_value=datetime.date(tahun, 1, 1),
                            max_value=datetime.date(tahun, 12, 31),
                            key=key_date,
                            label_visibility="collapsed",
                        )
                        if tgl:
                            bln_aktual = tgl.month
                            mgg_aktual = get_minggu_dari_tanggal(tgl)
                            st.session_state[key_bln_ak] = bln_aktual
                            st.session_state[key_mgg_ak] = mgg_aktual
                        else:
                            st.session_state.pop(key_bln_ak, None)
                            st.session_state.pop(key_mgg_ak, None)
                    else:
                        # Dropdown bulan & minggu
                        col_b, col_m = st.columns(2)
                        with col_b:
                            bln_aktual = st.selectbox(
                                "Bulan",
                                options=list(range(1, 13)),
                                format_func=lambda x: BULAN_NAMA[x-1],
                                index=bln - 1,
                                key=key_bln_ak,
                                label_visibility="collapsed",
                            )
                        with col_m:
                            mgg_aktual = st.selectbox(
                                "Minggu",
                                options=[1, 2, 3, 4],
                                format_func=lambda x: f"Minggu {x}",
                                index=mg - 1,
                                key=key_mgg_ak,
                                label_visibility="collapsed",
                            )

                with col_status_preview:
                    bln_ak = st.session_state.get(key_bln_ak)
                    mgg_ak = st.session_state.get(key_mgg_ak)
                    if bln_ak and mgg_ak:
                        status = hitung_status(bln, mg, bln_ak, mgg_ak)
                        warna  = status_color(status)
                        st.markdown(
                            f"<p style='color:{warna};font-family:IBM Plex Mono,monospace;"
                            f"font-size:12px;padding-top:8px;font-weight:700;'>{status}</p>",
                            unsafe_allow_html=True,
                        )
                    elif sudah_lewat_flag:
                        st.markdown(
                            "<p style='color:#ef4444;font-family:IBM Plex Mono,monospace;"
                            "font-size:12px;padding-top:8px;font-weight:700;'>❌ Tidak Terlaksana</p>",
                            unsafe_allow_html=True,
                        )
                    else:
                        st.markdown(
                            "<p style='color:#475569;font-family:IBM Plex Mono,monospace;"
                            "font-size:12px;padding-top:8px;'>⏳ Belum</p>",
                            unsafe_allow_html=True,
                        )

    st.markdown("<hr style='border-color:#1e2a45;margin:24px 0'>", unsafe_allow_html=True)

    # ── Step 2: Tombol Evaluasi ───────────────────────────────────────────────
    step_badge(2, "Evaluasi Realisasi")

    if st.button("📊 Jalankan Evaluasi", type="primary"):
        evaluasi = []
        for slot in semua_slot:
            nama = slot["nama"]
            bln  = slot["bulan_rencana"]
            mg   = slot["minggu_rencana"]
            key_bln_ak = f"bln_{nama}_{bln}_{mg}"
            key_mgg_ak = f"mgg_{nama}_{bln}_{mg}"

            bln_ak = st.session_state.get(key_bln_ak)
            mgg_ak = st.session_state.get(key_mgg_ak)

            if bln_ak and mgg_ak:
                status = hitung_status(bln, mg, bln_ak, mgg_ak)
                realisasi_label = f"{BULAN_NAMA[bln_ak-1]} Minggu {mgg_ak}"
            elif sudah_lewat(bln, mg):
                status = "❌ Tidak Terlaksana"
                realisasi_label = "-"
            else:
                status = "⏳ Belum"
                realisasi_label = "-"

            evaluasi.append({
                "nama"            : nama,
                "bulan_rencana"   : bln,
                "minggu_rencana"  : mg,
                "rencana_label"   : f"{BULAN_NAMA[bln-1]} Minggu {mg}",
                "realisasi_label" : realisasi_label,
                "status"          : status,
            })

        st.session_state["ins_evaluasi"] = evaluasi

    if "ins_evaluasi" not in st.session_state:
        st.info("Tekan tombol **Jalankan Evaluasi** untuk melihat hasil.")
        return

    evaluasi = st.session_state["ins_evaluasi"]

    # ── Ringkasan Statistik ───────────────────────────────────────────────────
    total        = len(evaluasi)
    n_tepat      = sum(1 for e in evaluasi if "Tepat"        in e["status"])
    n_terlambat  = sum(1 for e in evaluasi if "Terlambat"    in e["status"])
    n_cepat      = sum(1 for e in evaluasi if "Lebih Cepat"  in e["status"])
    n_tidak      = sum(1 for e in evaluasi if "Tidak"        in e["status"])
    n_belum      = sum(1 for e in evaluasi if "Belum"        in e["status"])
    terlaksana   = n_tepat + n_terlambat + n_cepat

    pct = lambda x: f"{x/total*100:.1f}%" if total > 0 else "0%"

    st.markdown("""
    <p style='color:#94a3b8;font-size:11px;font-family:IBM Plex Mono,monospace;
    letter-spacing:1px;margin-bottom:12px;'>RINGKASAN EVALUASI</p>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4, c5 = st.columns(5)
    def metric_box(col, label, nilai, warna, pct_val=""):
        col.markdown(f"""
        <div style="background:#0f1628;border:1px solid #1e2a45;border-radius:8px;
                    padding:14px;text-align:center;">
            <p style="color:{warna};font-size:22px;font-weight:700;
                      font-family:IBM Plex Mono,monospace;margin:0;">{nilai}</p>
            <p style="color:#64748b;font-size:10px;font-family:IBM Plex Mono,monospace;
                      margin:4px 0 0 0;letter-spacing:1px;">{label}</p>
            <p style="color:{warna};font-size:11px;font-family:IBM Plex Mono,monospace;
                      margin:2px 0 0 0;opacity:0.7;">{pct_val}</p>
        </div>
        """, unsafe_allow_html=True)

    metric_box(c1, "TEPAT",         n_tepat,     "#22c55e", pct(n_tepat))
    metric_box(c2, "TERLAMBAT",     n_terlambat, "#f59e0b", pct(n_terlambat))
    metric_box(c3, "LEBIH CEPAT",   n_cepat,     "#38bdf8", pct(n_cepat))
    metric_box(c4, "TIDAK TERLAKSANA", n_tidak,  "#ef4444", pct(n_tidak))
    metric_box(c5, "BELUM",         n_belum,     "#64748b", pct(n_belum))

    st.markdown("<br>", unsafe_allow_html=True)

    # Progress bar realisasi
    pct_terlaksana = terlaksana / total * 100 if total > 0 else 0
    st.markdown(f"""
    <div style="margin-bottom:20px;">
        <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
            <span style="color:#94a3b8;font-size:11px;font-family:IBM Plex Mono,monospace;">
                TINGKAT REALISASI
            </span>
            <span style="color:#f8fafc;font-size:11px;font-family:IBM Plex Mono,monospace;
                         font-weight:700;">
                {terlaksana}/{total} ({pct_terlaksana:.1f}%)
            </span>
        </div>
        <div style="background:#1e2a45;border-radius:4px;height:8px;">
            <div style="background:linear-gradient(90deg,#22c55e,#38bdf8);
                        border-radius:4px;height:8px;width:{pct_terlaksana:.1f}%;
                        transition:width 0.3s;"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#1e2a45;margin:8px 0 20px 0'>", unsafe_allow_html=True)

    # ── Tabel Detail Evaluasi ─────────────────────────────────────────────────
    step_badge(3, "Tabel Detail Evaluasi")

    # Filter per mesin
    mesin_list = list({e["nama"] for e in evaluasi})
    mesin_filter = st.selectbox(
        "Filter Mesin",
        options=["Semua Mesin"] + mesin_list,
        key="filter_mesin_evaluasi",
    )

    # Filter status
    status_filter = st.selectbox(
        "Filter Status",
        options=["Semua Status", "✅ Tepat", "⚠️ Terlambat", "⚡ Lebih Cepat",
                 "❌ Tidak Terlaksana", "⏳ Belum"],
        key="filter_status_evaluasi",
    )

    # Apply filter
    data_tampil = evaluasi
    if mesin_filter != "Semua Mesin":
        data_tampil = [e for e in data_tampil if e["nama"] == mesin_filter]
    if status_filter != "Semua Status":
        data_tampil = [e for e in data_tampil if e["status"] == status_filter]

    # Render tabel
    header_css = ("color:#f59e0b;font-size:10px;font-family:IBM Plex Mono,monospace;"
                  "letter-spacing:1px;padding:8px 10px;border-bottom:1px solid #1e2a45;"
                  "text-align:center;")
    cell_css   = ("color:#f8fafc;font-size:12px;font-family:IBM Plex Mono,monospace;"
                  "padding:7px 10px;text-align:center;border-bottom:1px solid #0f1628;")
    name_css   = ("color:#f8fafc;font-size:12px;font-family:IBM Plex Mono,monospace;"
                  "padding:7px 10px;text-align:left;border-bottom:1px solid #0f1628;"
                  "border-right:1px solid #1e2a45;")

    rows_html = ""
    for e in data_tampil:
        warna  = status_color(e["status"])
        rows_html += f"""
        <tr>
          <td style="{name_css}">{e['nama']}</td>
          <td style="{cell_css}">{e['rencana_label']}</td>
          <td style="{cell_css}">{e['realisasi_label']}</td>
          <td style="{cell_css};color:{warna};font-weight:700;">{e['status']}</td>
        </tr>
        """

    if not rows_html:
        rows_html = f"""
        <tr><td colspan="4" style="{cell_css};color:#475569;">
            Tidak ada data yang sesuai filter.
        </td></tr>
        """

    st.html(f"""
    <div style="overflow-x:auto;margin-top:12px;">
      <table style="border-collapse:collapse;background:#0a0e1a;width:100%;
                    font-family:IBM Plex Mono,monospace;">
        <thead>
          <tr>
            <th style="{header_css};text-align:left;border-right:1px solid #1e2a45;">Mesin</th>
            <th style="{header_css};">Rencana</th>
            <th style="{header_css};">Realisasi</th>
            <th style="{header_css};">Status</th>
          </tr>
        </thead>
        <tbody>{rows_html}</tbody>
      </table>
    </div>
    <p style="color:#475569;font-size:10px;font-family:IBM Plex Mono,monospace;
              margin-top:8px;">Menampilkan {len(data_tampil)} dari {len(evaluasi)} jadwal</p>
    """)