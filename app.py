import streamlit as st
st.set_page_config(
    page_title="MachineTrack",
    page_icon="⚙️",
    layout="wide",
    initial_sidebar_state="expanded",
)

from modules import database, dashboard, data_kerusakan, identifikasi_distribusi, goodness_of_fit
from modules import theme, inspection_interval, data_inspeksi

theme.inject()
database.init_db()

st.sidebar.markdown("""
<div class="sidebar-brand">
    <h2>⚙ MachineTrack</h2>
    <p>Failure Management System</p>
</div>
""", unsafe_allow_html=True)

MENU = {
    "📊  Dashboard"               : "dashboard",
    "📋  Data Kerusakan"          : "data_kerusakan",
    "🔍  Identifikasi Distribusi" : "identifikasi",
    "📐  Goodness of Fit"         : "gof",
    "🗓️  Interval Inspeksi"       : "inspeksi",
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