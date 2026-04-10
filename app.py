import streamlit as st
st.set_page_config(
    page_title="MachineTrack",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

import datetime
from modules import database, dashboard, data_kerusakan, identifikasi_distribusi, goodness_of_fit
from modules import theme, inspection_interval, data_inspeksi

theme.inject()
database.init_db()

# ── Sidebar brand ─────────────────────────────────────────────────────────────
st.sidebar.markdown("""
<div class="sidebar-brand">
    <h2>⚙ MachineTrack</h2>
    <p>Failure Management System</p>
</div>
""", unsafe_allow_html=True)

# ── Reminder Inspeksi di Sidebar ─────────────────────────────────────────────

def get_minggu_dari_hari(day: int) -> int:
    if day <= 7:  return 1
    if day <= 14: return 2
    if day <= 21: return 3
    return 4

def estimasi_tanggal_inspeksi(tahun: int, bulan: int, minggu: int) -> datetime.date:
    """Perkiraan tanggal tengah dari minggu inspeksi (hari ke-4 dari minggu tersebut)."""
    hari_mulai = (minggu - 1) * 7 + 1
    hari_target = hari_mulai + 3   # hari ke-4 dalam minggu itu
    import calendar
    max_hari = calendar.monthrange(tahun, bulan)[1]
    hari_target = min(hari_target, max_hari)
    return datetime.date(tahun, bulan, hari_target)

def render_sidebar_reminder():
    try:
        today       = datetime.date.today()
        tahun_skrg  = today.year
        bulan_skrg  = today.month
        minggu_skrg = get_minggu_dari_hari(today.day)

        # Ambil semua jadwal tahun ini yang belum terlaksana
        semua_jadwal = database.get_semua_jadwal_belum_terlaksana(tahun_skrg)
        if not semua_jadwal:
            return

        peringatan  = []   # sisa ≤ 3 hari
        terlewat    = []   # sudah lewat, belum dilakukan

        for jdw in semua_jadwal:
            tgl_est = estimasi_tanggal_inspeksi(tahun_skrg, jdw["bulan"], jdw["minggu"])
            selisih = (tgl_est - today).days

            if selisih < 0:
                # Sudah lewat
                terlewat.append({**jdw, "selisih": selisih, "tgl_est": tgl_est})
            elif selisih <= 3:
                # Mendekati
                peringatan.append({**jdw, "selisih": selisih, "tgl_est": tgl_est})

        if not peringatan and not terlewat:
            return

        st.sidebar.markdown("<hr style='border-color:#e7e0d6;margin:8px 0'>", unsafe_allow_html=True)
        st.sidebar.markdown(
            "<p style='color:#78716c;font-size:10px;font-family:IBM Plex Mono,monospace;"
            "letter-spacing:1px;margin:0 0 6px 0;'>🔔 REMINDER INSPEKSI</p>",
            unsafe_allow_html=True,
        )

        BULAN_NAMA = ["","Jan","Feb","Mar","Apr","Mei","Jun",
                      "Jul","Agt","Sep","Okt","Nov","Des"]

        # Terlewat — merah
        for t in terlewat[:3]:   # maksimal 3 item agar sidebar tidak terlalu panjang
            hari_lalu = abs(t["selisih"])
            label_waktu = f"{hari_lalu} hari lalu" if hari_lalu > 0 else "kemarin"
            st.sidebar.markdown(f"""
            <div style="background:#fef2f2;border-left:3px solid #dc2626;border-radius:4px;
                        padding:8px 10px;margin-bottom:6px;">
                <p style="color:#dc2626;font-size:10px;font-weight:700;
                          font-family:IBM Plex Mono,monospace;margin:0 0 2px 0;">
                    ❌ TERLEWAT · {label_waktu}</p>
                <p style="color:#1c1917;font-size:11px;
                          font-family:IBM Plex Mono,monospace;margin:0;font-weight:600;">
                    {t['mesin']}</p>
                <p style="color:#57534e;font-size:10px;
                          font-family:IBM Plex Mono,monospace;margin:0;">
                    {BULAN_NAMA[t['bulan']]} · Minggu {t['minggu']}</p>
            </div>
            """, unsafe_allow_html=True)

        # Mendekati — kuning/oranye
        for p in peringatan[:3]:
            if p["selisih"] == 0:
                label_waktu = "Hari ini!"
                warna_bg    = "#fff7ed"
                warna_border= "#ea580c"
                warna_teks  = "#ea580c"
                ikon        = "⚡"
            elif p["selisih"] == 1:
                label_waktu = "Besok"
                warna_bg    = "#fffbeb"
                warna_border= "#d97706"
                warna_teks  = "#d97706"
                ikon        = "⚠️"
            else:
                label_waktu = f"{p['selisih']} hari lagi"
                warna_bg    = "#fefce8"
                warna_border= "#ca8a04"
                warna_teks  = "#ca8a04"
                ikon        = "🔔"

            st.sidebar.markdown(f"""
            <div style="background:{warna_bg};border-left:3px solid {warna_border};
                        border-radius:4px;padding:8px 10px;margin-bottom:6px;">
                <p style="color:{warna_teks};font-size:10px;font-weight:700;
                          font-family:IBM Plex Mono,monospace;margin:0 0 2px 0;">
                    {ikon} {label_waktu.upper()}</p>
                <p style="color:#1c1917;font-size:11px;
                          font-family:IBM Plex Mono,monospace;margin:0;font-weight:600;">
                    {p['mesin']}</p>
                <p style="color:#57534e;font-size:10px;
                          font-family:IBM Plex Mono,monospace;margin:0;">
                    {BULAN_NAMA[p['bulan']]} · Minggu {p['minggu']}</p>
            </div>
            """, unsafe_allow_html=True)

        # Jika ada lebih dari 3 item, tampilkan ringkasan
        total_reminder = len(terlewat) + len(peringatan)
        if total_reminder > 6:
            sisa = total_reminder - 6
            st.sidebar.markdown(
                f"<p style='color:#78716c;font-size:10px;font-family:IBM Plex Mono,monospace;"
                f"text-align:center;margin:4px 0;'>+{sisa} jadwal lainnya</p>",
                unsafe_allow_html=True,
            )

        st.sidebar.markdown("<hr style='border-color:#e7e0d6;margin:8px 0'>", unsafe_allow_html=True)

    except Exception:
        # Jika fungsi DB belum ada, diam saja — tidak crash
        pass

render_sidebar_reminder()

# ── Menu ──────────────────────────────────────────────────────────────────────
MENU = {
    "📊  Dashboard"               : "dashboard",
    "📋  Data Kerusakan"          : "data_kerusakan",
    "🔍  Identifikasi Distribusi" : "identifikasi",
    "📐  Goodness of Fit"         : "gof",
    "🗓️  Rencana Inspeksi"        : "inspeksi",
    "📝  Data Inspeksi"           : "data_inspeksi",
}

choice = st.sidebar.radio("Menu", list(MENU.keys()), label_visibility="collapsed")
page   = MENU[choice]

st.sidebar.markdown("<div style='flex:1'></div>", unsafe_allow_html=True)
st.sidebar.markdown("""
<div class="sidebar-version">v2.0.0 · MachineTrack</div>
""", unsafe_allow_html=True)

if page == "dashboard":
    dashboard.show()
elif page == "data_kerusakan":
    data_kerusakan.show()
elif page == "identifikasi":
    identifikasi_distribusi.show()
elif page == "gof":
    goodness_of_fit.show()
elif page == "inspeksi":
    inspection_interval.show()
elif page == "data_inspeksi":
    data_inspeksi.show()