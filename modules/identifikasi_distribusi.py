import streamlit as st
import pandas as pd
import math
from modules import database
from modules.reliability import compute_index_of_fit
from modules.theme import page_header, step_badge

def show():
    # POIN 1: hapus subtitle "Index of Fit berbasis Median Rank Regression · Benard's Approximation"
    page_header("🔍", "Identifikasi Distribusi", "")

    tab_mesin, tab_manual = st.tabs(["🏭  Dari Database (TTR)", "🧮  Input Manual (TTF/TTR)"])

    with tab_mesin:
        machines = database.get_machine_names()
        if not machines:
            st.warning("Belum ada data mesin.")
        else:
            step_badge("01", "Pilih Mesin & Jenis Data")
            c1, c2 = st.columns(2)
            sel_mesin = c1.selectbox("Mesin", machines, key="mod3_mesin")
            data_type = c2.radio("Jenis Data", ["TTF", "TTR"], horizontal=True)

            if sel_mesin:
                m = database.get_machine(sel_mesin)
                st.info(f"**{sel_mesin}** — {m['merek'] or '—'} {m['tipe'] or '—'} (Tahun {m['tahun'] or '—'})")

            st.markdown("---")
            step_badge("02", "Input Data")
            raw_data = []

            if data_type == "TTR":
                ttr_list = database.get_ttr_by_machine(sel_mesin)
                if not ttr_list:
                    st.warning("Tidak ada data TTR untuk mesin ini.")
                else:
                    st.success(f"✅ {len(ttr_list)} data TTR ditemukan dari database.")
                    df_ttr = pd.DataFrame({"No": range(1, len(ttr_list)+1), "TTR (jam)": ttr_list})
                    st.dataframe(df_ttr, use_container_width=False, hide_index=True)
                    raw_data = ttr_list
            else:
                all_failures = database.get_failures_by_machine(sel_mesin)
                n_failures   = len([r for r in all_failures if r["failure_type"] == "Corrective"])
                max_ttf      = max(n_failures - 1, 1)
                st.info(f"Mesin **{sel_mesin}** memiliki **{n_failures} data kerusakan**. Maksimal TTF: **{max_ttf} data**.")

                if ("ttf_table" not in st.session_state or
                        st.session_state.get("ttf_mesin") != sel_mesin):
                    st.session_state["ttf_table"] = [{"No": i+1, "TTF (jam)": ""} for i in range(max_ttf)]
                    st.session_state["ttf_mesin"] = sel_mesin

                df_input = pd.DataFrame(st.session_state["ttf_table"])
                edited   = st.data_editor(
                    df_input, use_container_width=False, hide_index=True, num_rows="fixed",
                    column_config={
                        "No":        st.column_config.NumberColumn("No", disabled=True, width="small"),
                        "TTF (jam)": st.column_config.NumberColumn("TTF (jam)", min_value=0.0, step=0.01, width="medium"),
                    },
                    key=f"ttf_editor_{sel_mesin}"
                )
                st.session_state["ttf_table"] = edited.to_dict("records")
                for row in edited.to_dict("records"):
                    try:
                        val = float(row["TTF (jam)"])
                        if val > 0:
                            raw_data.append(val)
                    except:
                        pass
                if raw_data:
                    st.caption(f"✅ {len(raw_data)} data valid siap dihitung.")

            st.markdown("---")
            step_badge("03", "Hitung Index of Fit")
            if st.button("🔍  Hitung Index of Fit", disabled=len(raw_data) < 2, key="btn_hitung_db"):
                result = compute_index_of_fit(raw_data)
                st.session_state["mod1_result"] = result
                st.session_state["mod1_mesin"]  = sel_mesin
                st.session_state["mod1_dtype"]  = data_type

            if ("mod1_result" in st.session_state and
                    st.session_state.get("mod1_mesin") == sel_mesin):
                _tampilkan_hasil(st.session_state["mod1_result"])

    with tab_manual:
        step_badge("01", "Input Data TTF / TTR Manual")
        st.caption("Masukkan data langsung untuk verifikasi — tidak perlu ada mesin di database.")

        if "manual_rows" not in st.session_state:
            st.session_state["manual_rows"] = [{"No": i+1, "Nilai (jam)": None} for i in range(5)]

        c1, c2, _ = st.columns([1, 1, 4])
        if c1.button("➕  Tambah Baris", key="btn_add_row"):
            n = len(st.session_state["manual_rows"])
            st.session_state["manual_rows"].append({"No": n+1, "Nilai (jam)": None})
            st.rerun()
        if c2.button("➖  Kurang Baris", key="btn_del_row",
                     disabled=len(st.session_state["manual_rows"]) <= 1):
            st.session_state["manual_rows"].pop()
            for i, r in enumerate(st.session_state["manual_rows"]):
                r["No"] = i + 1
            st.rerun()

        df_manual = pd.DataFrame(st.session_state["manual_rows"])
        edited_manual = st.data_editor(
            df_manual, use_container_width=False, hide_index=True, num_rows="fixed",
            column_config={
                "No":          st.column_config.NumberColumn("No", disabled=True, width="small"),
                "Nilai (jam)": st.column_config.NumberColumn("Nilai (jam)", min_value=0.0001, step=0.01, width="medium"),
            },
            key="manual_editor"
        )
        saved = edited_manual.to_dict("records")
        for i, r in enumerate(saved):
            r["No"] = i + 1
        st.session_state["manual_rows"] = saved

        raw_manual = []
        for row in saved:
            try:
                val = float(row["Nilai (jam)"])
                if val > 0:
                    raw_manual.append(val)
            except:
                pass

        if raw_manual:
            st.caption(f"✅ {len(raw_manual)} data valid: {sorted(raw_manual)}")
        else:
            st.caption("⚠️ Belum ada data valid.")

        st.markdown("---")
        step_badge("02", "Hitung Index of Fit")
        dtype_manual = st.radio("Jenis Data", ["TTF", "TTR"], horizontal=True, key="dtype_manual")

        if st.button("🔍  Hitung Index of Fit", disabled=len(raw_manual) < 2, key="btn_hitung_manual"):
            result_m = compute_index_of_fit(raw_manual)
            st.session_state["mod1_result"]   = result_m
            st.session_state["mod1_mesin"]    = f"[Manual {dtype_manual}]"
            st.session_state["mod1_dtype"]    = dtype_manual
            st.session_state["manual_result"] = result_m

        if "manual_result" in st.session_state:
            _tampilkan_hasil(st.session_state["manual_result"])
            st.info("➡️ Lanjutkan ke menu **Goodness of Fit** untuk pengujian statistik.")


def _tampilkan_hasil(result):
    best = result["best"]
    st.markdown("---")
    step_badge("✓", "Hasil Index of Fit")

    rows_r = []
    for name, res in sorted(result["results"].items(), key=lambda x: -x[1]["R2"]):
        rows_r.append({
            "Distribusi":       name,
            "r (Index of Fit)": round(float(res["r"]), 4),
            "Status":           "✅ Terpilih" if name == best else "—",
        })
    st.dataframe(pd.DataFrame(rows_r), use_container_width=False, hide_index=True)

    r_best = round(float(result["results"][best]["r"]), 4)

    # POIN 2: ganti warna teks di kotak distribusi terpilih — coklat tembaga & hitam pekat agar kontras
    st.markdown(f"""
    <div style="background:#fef3c7;border:1px solid #b45309;
    border-left:4px solid #b45309;border-radius:8px;padding:0.8rem 1.2rem;margin:0.8rem 0;">
        <span style="font-family:'IBM Plex Mono',monospace;font-size:0.72rem;
        color:#92400e;font-weight:700;letter-spacing:0.06em;text-transform:uppercase;">
        Distribusi Terpilih</span>
        <p style="font-family:'IBM Plex Mono',monospace;font-size:1.2rem;
        font-weight:700;color:#1c1917;margin:4px 0 0 0;">
        {best} <span style="font-size:0.85rem;color:#57534e;font-weight:400;">
        r = {r_best}</span></p>
    </div>
    """, unsafe_allow_html=True)

    step_badge("▸", "Parameter Distribusi Terpilih")
    res_best = result["results"][best]
    st.caption(f"Slope (b) = {res_best['b']}  ·  Intercept (a) = {res_best['a']}")
    cols = st.columns(len(res_best["params"]))
    for idx, (k, v) in enumerate(res_best["params"].items()):
        cols[idx].metric(f"Parameter {k}", v)

    with st.expander(f"📋  Tabel Median Rank & Transformasi — {best}"):
        t = result["t"]; F = result["F"]; n = len(t)

        if best == "Normal":
            xi_list = t
            yi_list = [_norm_inv(f) for f in F]
            xi_label, yi_label = "xᵢ = tᵢ", "yᵢ = Φ⁻¹(F(tᵢ))"
        elif best == "Lognormal":
            xi_list = [math.log(v) for v in t]
            yi_list = [_norm_inv(f) for f in F]
            xi_label, yi_label = "xᵢ = ln(tᵢ)", "yᵢ = Φ⁻¹(F(tᵢ))"
        elif best == "Weibull":
            xi_list = [math.log(v) for v in t]
            yi_list = [math.log(math.log(1/(1-f))) for f in F]
            xi_label, yi_label = "xᵢ = ln(tᵢ)", "yᵢ = ln(ln(1/(1−F)))"
        else:
            xi_list = t
            yi_list = [-math.log(1-f) for f in F]
            xi_label, yi_label = "xᵢ = tᵢ", "yᵢ = −ln(1−F(tᵢ))"

        rows_mr = []
        for i in range(n):
            xi, yi = xi_list[i], yi_list[i]
            rows_mr.append({
                "i": i+1, "tᵢ": round(t[i],4), "F(tᵢ)": round(F[i],4),
                xi_label: round(xi,4), yi_label: round(yi,4),
                "xᵢ·yᵢ": round(xi*yi,4), "xᵢ²": round(xi**2,4), "yᵢ²": round(yi**2,4),
            })
        total_row = {
            "i": "Σ", "tᵢ": "", "F(tᵢ)": "",
            xi_label: round(sum(xi_list),4), yi_label: round(sum(yi_list),4),
            "xᵢ·yᵢ": round(sum(r["xᵢ·yᵢ"] for r in rows_mr),4),
            "xᵢ²":   round(sum(r["xᵢ²"]   for r in rows_mr),4),
            "yᵢ²":   round(sum(r["yᵢ²"]   for r in rows_mr),4),
        }
        df_mr = pd.concat([pd.DataFrame(rows_mr), pd.DataFrame([total_row])], ignore_index=True)
        st.dataframe(df_mr, use_container_width=True, hide_index=True)


def _norm_inv(p):
    if p <= 0: return -math.inf
    if p >= 1: return  math.inf
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
          1.383577518672690e+02, -3.066479806614716e+01,  2.506628277459239e+00]
    b = [-5.447609879822406e+01,  1.615858368580409e+02, -1.556989798598866e+02,
          6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00,  4.374664141464968e+00,  2.938163982698783e+00]
    d = [ 7.784695709041462e-03,  3.224671290700398e-01,  2.445134137142996e+00,
          3.754408661907416e+00]
    p_low, p_high = 0.02425, 1 - 0.02425
    if p < p_low:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
               ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    elif p <= p_high:
        q = p - 0.5; r = q*q
        return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / \
               (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
    else:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / \
                ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)