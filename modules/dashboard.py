import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from modules import database
from modules.theme import page_header, step_badge

# ── Warna chart disesuaikan tema terang ───────────────────
PLOT_LAYOUT = dict(
    plot_bgcolor="#ffffff",
    paper_bgcolor="#ffffff",
    font=dict(family="Nunito, sans-serif", color="#44403c", size=12),
    margin=dict(l=0, r=0, t=20, b=0),
    xaxis=dict(gridcolor="#e8e5e1", linecolor="#d6cfc6", tickfont=dict(size=11), tickcolor="#78716c"),
    yaxis=dict(gridcolor="#e8e5e1", linecolor="#d6cfc6", tickfont=dict(size=11), tickcolor="#78716c"),
    legend=dict(bgcolor="rgba(255,255,255,0.8)", font=dict(size=11), bordercolor="#d6cfc6", borderwidth=1),
)

def show():
    page_header("📊", "Dashboard", "Overview kerusakan mesin secara keseluruhan atau per mesin")

    machines = database.get_machine_names()
    if not machines:
        st.warning("Belum ada data mesin. Silakan tambahkan mesin di menu **Data Kerusakan**.")
        return

    # ── Filter ────────────────────────────────────────────
    c1, c2 = st.columns([4, 1])
    with c2:
        show_all = st.checkbox("Semua mesin", value=True)
    with c1:
        if show_all:
            selected = machines
        else:
            selected = st.multiselect("Pilih mesin", machines, default=machines[:1])

    if not selected:
        st.info("Pilih minimal satu mesin.")
        return

    all_rows = database.get_all_failures()
    if not all_rows:
        st.info("Belum ada data kerusakan.")
        return

    df = pd.DataFrame([dict(r) for r in all_rows])
    df = df[df["mesin"].isin(selected)]
    if df.empty:
        st.info("Tidak ada data untuk mesin yang dipilih.")
        return

    df["failure_start_date"] = pd.to_datetime(df["failure_start_date"], errors="coerce")

    # ── KPI Cards ─────────────────────────────────────────
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total Laporan",      len(df))
    c2.metric("Corrective",         len(df[df["failure_type"] == "Corrective"]))
    c3.metric("Preventive",         len(df[df["failure_type"] == "Preventive"]))
    c4.metric("Total Repair Hours", f"{df['total_repair_hours'].sum():.1f} h")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── Chart row 1 ───────────────────────────────────────
    col1, col2 = st.columns([3, 2])

    with col1:
        st.subheader("Kerusakan per Mesin")
        grp = df.groupby(["mesin", "failure_type"]).size().reset_index(name="count")
        fig = px.bar(
            grp, x="mesin", y="count", color="failure_type", barmode="group",
            color_discrete_map={"Corrective": "#b91c1c", "Preventive": "#15803d"},
            labels={"mesin": "Mesin", "count": "Jumlah", "failure_type": "Tipe"},
        )
        fig.update_layout(**PLOT_LAYOUT)
        fig.update_traces(marker_line_width=0)
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        st.subheader("Proporsi Jenis")
        pie = df["failure_type"].value_counts().reset_index()
        pie.columns = ["failure_type", "count"]
        fig2 = px.pie(
            pie, names="failure_type", values="count", hole=0.5,
            color="failure_type",
            color_discrete_map={"Corrective": "#b91c1c", "Preventive": "#15803d"},
        )
        fig2.update_layout(**{**PLOT_LAYOUT, "showlegend": True})
        fig2.update_traces(textfont=dict(family="Nunito, sans-serif", size=12))
        st.plotly_chart(fig2, use_container_width=True)

    # ── Chart row 2 ───────────────────────────────────────
    st.subheader("Tren Kerusakan Bulanan")
    df["month"] = df["failure_start_date"].dt.to_period("M").astype(str)
    trend = df.groupby("month").size().reset_index(name="total")
    fig3 = go.Figure()
    fig3.add_trace(go.Scatter(
        x=trend["month"], y=trend["total"],
        mode="lines+markers",
        line=dict(color="#b45309", width=2.5),
        marker=dict(color="#b45309", size=8, line=dict(color="#ffffff", width=2)),
        fill="tozeroy",
        fillcolor="rgba(180,83,9,0.08)",
    ))
    fig3.update_layout(**{**PLOT_LAYOUT, "margin": dict(l=0, r=0, t=10, b=0)})
    st.plotly_chart(fig3, use_container_width=True)

    # ── Chart row 3 ───────────────────────────────────────
    st.subheader("Total Repair Hours per Mesin")
    hrs = df.groupby("mesin")["total_repair_hours"].sum().reset_index().sort_values("total_repair_hours")
    fig4 = go.Figure(go.Bar(
        x=hrs["total_repair_hours"], y=hrs["mesin"],
        orientation="h",
        marker=dict(
            color=hrs["total_repair_hours"],
            colorscale=[[0, "#fde68a"], [1, "#b45309"]],
            line=dict(width=0),
        ),
    ))
    fig4.update_layout(**{**PLOT_LAYOUT,
        "xaxis": dict(gridcolor="#e8e5e1", title="Total Jam", tickfont=dict(size=11)),
        "yaxis": dict(gridcolor="#e8e5e1", title="", tickfont=dict(size=11)),
    })
    st.plotly_chart(fig4, use_container_width=True)