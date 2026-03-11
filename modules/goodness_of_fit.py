import streamlit as st
import pandas as pd
import math
from modules.reliability import compute_gof
from modules.theme import page_header, step_badge, verdict

# ── Helper MTTF/MTTR ─────────────────────────────────────────────────────────

def _gamma(x: float) -> float:
    """Lanczos approximation for Gamma function."""
    if x < 0.5:
        return math.pi / (math.sin(math.pi * x) * _gamma(1 - x))
    x -= 1
    g = 7
    c = [0.99999999999980993, 676.5203681218851, -1259.1392167224028,
         771.32342877765313, -176.61502916214059, 12.507343278686905,
         -0.13857109526572012, 9.9843695780195716e-6, 1.5056327351493116e-7]
    t = x + g + 0.5
    s = c[0] + sum(c[i] / (x + i) for i in range(1, g + 2))
    return math.sqrt(2 * math.pi) * t ** (x + 0.5) * math.exp(-t) * s


def _regress(x, y):
    """Regresi linear, return (a, b) exact tanpa pembulatan."""
    n = len(x)
    sx = sum(x); sy = sum(y)
    sxy = sum(xi*yi for xi,yi in zip(x,y))
    sx2 = sum(xi**2 for xi in x)
    num = n*sxy - sx*sy
    den = n*sx2 - sx**2
    b = num/den if den != 0 else 0
    a = (sy - b*sx)/n
    return a, b

def _norm_inv(p):
    a = [0,-3.969683028665376e+01,2.209460984245205e+02,-2.759285104469687e+02,
         1.383577518672690e+02,-3.066479806614716e+01,2.506628277459239e+00]
    b = [0,-5.447609879822406e+01,1.615858368580409e+02,-1.556989798598866e+02,
         6.680131188771972e+01,-1.328068155288572e+01]
    c = [0,-7.784894002430293e-03,-3.223964580411365e-01,-2.400758277161838e+00,
         -2.549732539343734e+00,4.374664141464968e+00,2.938163982698783e+00]
    d = [0,7.784695709041462e-03,3.224671290700398e-01,2.445134137142996e+00,3.754408661907416e+00]
    p_low, p_high = 0.02425, 1 - 0.02425
    if p < p_low:
        q = math.sqrt(-2*math.log(p))
        return (((((c[1]*q+c[2])*q+c[3])*q+c[4])*q+c[5])*q+c[6])/((((d[1]*q+d[2])*q+d[3])*q+d[4])*q+1)
    elif p <= p_high:
        q = p-0.5; r = q*q
        return (((((a[1]*r+a[2])*r+a[3])*r+a[4])*r+a[5])*r+a[6])*q/(((((b[1]*r+b[2])*r+b[3])*r+b[4])*r+b[5])*r+1)
    else:
        q = math.sqrt(-2*math.log(1-p))
        return -(((((c[1]*q+c[2])*q+c[3])*q+c[4])*q+c[5])*q+c[6])/((((d[1]*q+d[2])*q+d[3])*q+d[4])*q+1)

def hitung_mttf(dist: str, t_data: list) -> float:
    """Hitung MTTF/MTTR dari data t raw — tanpa pembulatan di tengah proses."""
    n = len(t_data)
    t = sorted(t_data)
    F = [(i + 1 - 0.3) / (n + 0.4) for i in range(n)]

    if dist == "Normal":
        x = t
        y = [_norm_inv(f) for f in F]
        a, b = _regress(x, y)
        return -a/b if b != 0 else 0

    elif dist == "Lognormal":
        x = [math.log(v) for v in t]
        y = [_norm_inv(f) for f in F]
        a, b = _regress(x, y)
        mu    = -a/b
        sigma = 1/b
        return math.exp(mu + sigma**2/2)

    elif dist == "Weibull":
        x = [math.log(v) for v in t]
        y = [math.log(math.log(1/(1-f))) for f in F]
        a, b = _regress(x, y)
        beta = b
        eta  = math.exp(-a/b) if b != 0 else 0
        return eta * _gamma(1 + 1/beta)

    elif dist == "Eksponensial":
        x = t
        y = [-math.log(1-f) for f in F]
        a, b = _regress(x, y)
        return 1/b if b > 0 else 0

    return 0.0


def render_mttf_box(dist: str, params: dict, dtype: str, nilai: float, a: float = 0, b: float = 0):
    label   = "MTTR" if dtype == "TTR" else "MTTF"
    rumus_map = {
        "Weibull":      "η · Γ(1 + 1/β)",
        "Eksponensial": "1 / λ",
        "Normal":       "μ",
        "Lognormal":    "exp(μ + σ²/2)",
    }
    rumus = rumus_map.get(dist, "—")

    # POIN 3: sesuaikan warna dengan tema light mode (cream/amber)
    param_str = "  &nbsp;|&nbsp;  ".join(
        [f"<span style='color:#78716c'>{k}</span> = <span style='color:#b45309'>{v}</span>"
         for k, v in params.items()]
    )

    st.html(f"""
<div style="background:#fef9f0;border:1px solid #b4530944;border-radius:8px;
            padding:20px 24px;margin-top:8px;">
  <p style="color:#78716c;font-family:'IBM Plex Mono',monospace;font-size:11px;
            margin:0 0 4px 0;letter-spacing:2px;text-transform:uppercase;">
    {label} — Distribusi {dist}
  </p>
  <p style="color:#b45309;font-family:'IBM Plex Mono',monospace;font-size:36px;
            font-weight:700;margin:0;">{nilai:.4f}</p>
  <p style="color:#a8a29e;font-family:'IBM Plex Mono',monospace;font-size:11px;
            margin:6px 0 10px 0;">satuan waktu</p>
  <p style="color:#a8a29e;font-family:'IBM Plex Mono',monospace;font-size:11px;margin:0;">
    Rumus: <span style="color:#57534e;">{rumus}</span>
    &nbsp;&nbsp;·&nbsp;&nbsp; {param_str}
  </p>
</div>
""")


# ── Main show() ───────────────────────────────────────────────────────────────

def show():
    page_header("📐", "Goodness of Fit Test",
                "Pengujian statistik kesesuaian distribusi · α = 0.05")

    if "mod1_result" not in st.session_state:
        st.warning("⚠️ Jalankan **Modul 3 — Identifikasi Distribusi** terlebih dahulu.")
        return

    result   = st.session_state["mod1_result"]
    mesin    = st.session_state.get("mod1_mesin", "—")
    dtype    = st.session_state.get("mod1_dtype", "—")
    best     = result["best"]
    res_best = result["results"][best]

    # ── Info distribusi terpilih ───────────────────────────
    step_badge("01", "Distribusi yang Akan Diuji")
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Mesin",      mesin)
    c2.metric("Jenis Data", dtype)
    c3.metric("Distribusi", best)
    c4.metric("r (Index of Fit)", round(float(res_best["r"]), 4))

    method_map = {
        "Normal":       "Kolmogorov-Smirnov Test",
        "Lognormal":    "Kolmogorov-Smirnov Test",
        "Weibull":      "Mann's Test",
        "Eksponensial": "Bartlett Test",
    }
    st.info(f"📌 Metode uji: **{method_map[best]}**")

    cols = st.columns(len(res_best["params"]))
    for idx, (k, v) in enumerate(res_best["params"].items()):
        cols[idx].metric(f"Parameter {k}", v)

    st.markdown("---")
    step_badge("02", "Jalankan Goodness of Fit Test")

    if st.button("📐  Jalankan Goodness of Fit Test"):
        ranked = sorted(result["results"].items(), key=lambda x: -x[1]["R2"])
        gof_list = []
        for dist_name, _ in ranked:
            gof_i = compute_gof(result, dtype=dtype, override_best=dist_name)
            gof_i["distribusi"] = dist_name
            gof_i["R2"]         = result["results"][dist_name]["R2"]
            gof_list.append(gof_i)
            if gof_i["accept"]:
                break
        st.session_state["mod2_result"] = gof_list[-1]
        st.session_state["mod2_all"]    = gof_list

    if "mod2_result" not in st.session_state:
        return

    gof_all = st.session_state.get("mod2_all", [])

    # Ringkasan urutan pengujian (jika ada fallback)
    if len(gof_all) > 1:
        st.markdown("---")
        step_badge("03", "Urutan Pengujian (Fallback)")
        rows_seq = []
        for g in gof_all:
            rows_seq.append({
                "Distribusi":       g["distribusi"],
                "r (Index of Fit)": round(float(result["results"][g["distribusi"]]["r"]), 4),
                "Metode":           g["method"],
                "Keputusan":        "✅ Diterima" if g["accept"] else "❌ Ditolak",
            })
        st.dataframe(pd.DataFrame(rows_seq), use_container_width=False, hide_index=True)

    gof    = st.session_state["mod2_result"]
    best   = gof["distribusi"]
    step_n = "03" if len(gof_all) <= 1 else "04"

    st.markdown("---")
    step_badge(step_n, f"Hasil {gof['method']} — {best}")

    # ── KS Test ───────────────────────────────────────────
    if gof["method"] == "Kolmogorov-Smirnov Test":
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("D hitung",          gof["D_hitung"])
        c2.metric("D kritis (α=0.05)", gof["D_kritis"])
        c3.metric("μ (digunakan)",     gof["mu"])
        c4.metric("σ (digunakan)",     gof["sigma"])

        xi_label = "xᵢ = ln(tᵢ)" if best == "Lognormal" else "xᵢ = tᵢ"
        df_ks    = pd.DataFrame(gof["table"])

        if best == "Normal":
            df_ks = df_ks[["i","ti","xi","F_emp_low","F_emp_high","dev_sq","Zi","F_teoritis","D1","D2"]]
            df_ks = df_ks.rename(columns={
                "i": "i", "ti": "tᵢ", "xi": xi_label,
                "F_emp_low": "(i−1)/n", "F_emp_high": "i/n",
                "dev_sq": "(tᵢ−μ)²", "Zi": "Zᵢ",
                "F_teoritis": "Φ(Zᵢ)", "D1": "D₁(i)", "D2": "D₂(i)",
            })
        else:
            df_ks = df_ks[["i","ti","xi","F_emp_low","F_emp_high","Zi","F_teoritis","D1","D2"]]
            df_ks = df_ks.rename(columns={
                "i": "i", "ti": "tᵢ", "xi": xi_label,
                "F_emp_low": "(i−1)/n", "F_emp_high": "i/n",
                "Zi": "Zᵢ", "F_teoritis": "Φ(Zᵢ)", "D1": "D₁(i)", "D2": "D₂(i)",
            })
        st.dataframe(df_ks, use_container_width=True, hide_index=True)

        sym = "≤" if gof["accept"] else ">"
        st.markdown(f"""
<div style="background:#fef9f0;border:1px solid #b4530944;border-radius:8px;
padding:0.8rem 1.2rem;margin-top:0.5rem;font-family:'IBM Plex Mono',monospace;font-size:0.85rem;color:#1c1917;">
D hitung = <code>{gof['D_hitung']}</code> &nbsp;<b>{sym}</b>&nbsp; D kritis = <code>{gof['D_kritis']}</code>
</div>""", unsafe_allow_html=True)

    # ── Bartlett Test ──────────────────────────────────────
    elif gof["method"] == "Bartlett Test":
        df_bt = pd.DataFrame(gof["table"])
        df_bt = df_bt.rename(columns={
            "i": "i", "ti": "tᵢ", "xi=ln(ti)": "xᵢ = ln(tᵢ)",
            "k+1": "k+1", "2k": "2k", "6k": "6k",
            "ln(Σti/k)": "ln(Σtᵢ/k)", "Σxi(1/k)": "Σxᵢ·(1/k)",
        })
        st.dataframe(df_bt, use_container_width=True, hide_index=True)

        st.markdown("---")
        alpha = 0.05
        param_rows = [{
            "α": alpha, "α/2": alpha/2, "1−α/2": 1-alpha/2,
            "B": gof["B"],
            "χ²(1−α/2; k−1)": gof["chi_high"],
            "χ²(α/2; k−1)":   gof["chi_low"],
        }]
        st.dataframe(pd.DataFrame(param_rows), use_container_width=False, hide_index=True)

        in_out = "berada dalam rentang" if gof["accept"] else "di luar rentang"
        st.markdown(f"""
<div style="background:#fef9f0;border:1px solid #b4530944;border-radius:8px;
padding:0.8rem 1.2rem;margin-top:0.5rem;font-family:'IBM Plex Mono',monospace;font-size:0.85rem;color:#1c1917;">
B hitung = <code>{gof['B']}</code> &nbsp;·&nbsp;
Rentang kritis = [<code>{gof['chi_low']}</code> , <code>{gof['chi_high']}</code>]
&nbsp;·&nbsp; B <b>{in_out}</b>
</div>""", unsafe_allow_html=True)

    # ── Mann's Test ────────────────────────────────────────
    elif gof["method"] == "Mann's Test":
        df_mann = pd.DataFrame(gof["table"])
        df_mann = df_mann.rename(columns={
            "i": "i", "ti": "tᵢ", "xi=ln(ti)": "xᵢ = ln(tᵢ)",
            "1-(i-0.5)/(r+0.25)": "1−(i−0.5)/(r+0.25)",
            "-ln(1-F)": "−ln(1−F)", "Zi": "Zᵢ",
            "Mi=Zi+1-Zi": "Mᵢ = Zᵢ₊₁−Zᵢ",
            "Δln(ti)": "ln(tᵢ₊₁)−ln(tᵢ)",
            "Δln(ti)/Mi": "Δln(tᵢ)/Mᵢ",
        })
        st.dataframe(df_mann, use_container_width=True, hide_index=True)

        st.markdown("---")
        param_rows = [{
            "k₁": gof["k1"], "k₂": gof["k2"],
            "S1": gof["S1"], "S2": gof["S2"],
            "M hitung": gof["M"],
            "F kritis (α=0.05)": gof["F_kritis"],
        }]
        st.dataframe(pd.DataFrame(param_rows), use_container_width=False, hide_index=True)

        sym = "< F kritis" if gof["accept"] else "≥ F kritis"
        st.markdown(f"""
<div style="background:#fef9f0;border:1px solid #b4530944;border-radius:8px;
padding:0.8rem 1.2rem;margin-top:0.5rem;font-family:'IBM Plex Mono',monospace;font-size:0.85rem;color:#1c1917;">
M hitung = <code>{gof['M']}</code> &nbsp;<b>{sym}</b>&nbsp; F(0.05; {gof['k1']}; {gof['k2']}) = <code>{gof['F_kritis']}</code>
</div>""", unsafe_allow_html=True)

    # ── Verdict final ──────────────────────────────────────
    st.markdown("---")
    dtype_display = st.session_state.get("mod1_dtype", "—")
    if gof["accept"]:
        verdict(
            accept=True,
            title="H₀ Diterima",
            body=f"Data <b>{dtype_display}</b> mesin <b>{mesin}</b> mengikuti distribusi <b>{best}</b> "
                 f"pada taraf signifikansi α = 0.05. "
                 f"Distribusi ini valid digunakan untuk analisis reliability selanjutnya."
        )
    else:
        verdict(
            accept=False,
            title="H₀ Ditolak",
            body=f"Data <b>{dtype_display}</b> mesin <b>{mesin}</b> tidak terbukti mengikuti distribusi manapun "
                 f"pada taraf signifikansi α = 0.05. "
                 f"Tinjau kembali data atau tambah jumlah data."
        )

    # ── MTTF / MTTR ───────────────────────────────────────
    if gof["accept"]:
        st.markdown("---")
        label_step = "MTTR" if dtype == "TTR" else "MTTF"
        step_badge("04" if len(gof_all) <= 1 else "05", f"Hasil {label_step}")

        params = result["results"][best]["params"]
        t_data = result["t"]
        nilai  = hitung_mttf(best, t_data)
        render_mttf_box(best, params, dtype, nilai)