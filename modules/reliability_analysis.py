import streamlit as st
import math
from modules.reliability import r2, norm_cdf
from modules.theme import page_header, step_badge, verdict

# ── helpers ──────────────────────────────────────────────────────────────────

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


def _phi(z: float) -> float:
    """Standard normal PDF."""
    return math.exp(-0.5 * z * z) / math.sqrt(2 * math.pi)


# ── reliability functions per distribusi ────────────────────────────────────

def compute_reliability(dist: str, params: dict, t: float):
    """Return dict {R, F, f, h} untuk nilai t tunggal."""
    eps = 1e-12
    if t <= 0:
        return {"R": 1.0, "F": 0.0, "f": 0.0, "h": 0.0}

    if dist == "Weibull":
        beta, eta = params["beta"], params["eta"]
        R = math.exp(-((t / eta) ** beta))
        f = (beta / eta) * ((t / eta) ** (beta - 1)) * R
        h = (beta / eta) * ((t / eta) ** (beta - 1))
        F = 1 - R

    elif dist == "Eksponensial":
        lam = params["lambda"]
        R = math.exp(-lam * t)
        f = lam * R
        h = lam
        F = 1 - R

    elif dist == "Normal":
        mu, sigma = params["mu"], params["sigma"]
        z = (t - mu) / sigma
        F = norm_cdf(z)
        R = 1 - F
        f = _phi(z) / sigma
        h = f / R if R > eps else 0.0

    elif dist == "Lognormal":
        mu, sigma = params["mu"], params["sigma"]
        if t <= 0:
            return {"R": 1.0, "F": 0.0, "f": 0.0, "h": 0.0}
        z = (math.log(t) - mu) / sigma
        F = norm_cdf(z)
        R = 1 - F
        f = _phi(z) / (t * sigma)
        h = f / R if R > eps else 0.0

    else:
        return None

    return {"R": R, "F": F, "f": f, "h": h}


def compute_mttf(dist: str, params: dict) -> float:
    if dist == "Weibull":
        return params["eta"] * _gamma(1 + 1 / params["beta"])
    elif dist == "Eksponensial":
        return 1 / params["lambda"]
    elif dist == "Normal":
        return params["mu"]
    elif dist == "Lognormal":
        mu, sigma = params["mu"], params["sigma"]
        return math.exp(mu + sigma ** 2 / 2)
    return 0.0


def _build_t_range(params: dict, dist: str, n: int = 300):
    """Buat range t yang representatif untuk grafik."""
    if dist == "Weibull":
        t_max = params["eta"] * 4
    elif dist == "Eksponensial":
        t_max = (1 / params["lambda"]) * 5
    elif dist == "Normal":
        t_max = max(params["mu"] + 4 * params["sigma"], 1.0)
    elif dist == "Lognormal":
        mu, sigma = params["mu"], params["sigma"]
        t_max = math.exp(mu + 3 * sigma)
    else:
        t_max = 100
    t_min = t_max / 1000
    step = (t_max - t_min) / n
    return [t_min + i * step for i in range(n + 1)]


# ── chart builder (pure HTML/JS dengan Chart.js via CDN) ─────────────────────

def _line_chart_html(title: str, x_data, y_data, color: str, y_label: str, x_label: str = "t") -> str:
    x_js = str([round(v, 4) for v in x_data])
    y_js = str([round(v, 6) for v in y_data])
    chart_id = title.replace(" ", "_").replace("(", "").replace(")", "")
    return f"""
<div style="background:#0f1628;border:1px solid #1e2a45;border-radius:8px;padding:16px;margin-bottom:16px;">
  <p style="color:#f59e0b;font-family:'IBM Plex Mono',monospace;font-size:13px;margin:0 0 10px 0;letter-spacing:1px;">
    ▸ {title}
  </p>
  <canvas id="{chart_id}" height="180"></canvas>
</div>
<script>
(function(){{
  const ctx = document.getElementById('{chart_id}').getContext('2d');
  new Chart(ctx, {{
    type: 'line',
    data: {{
      labels: {x_js},
      datasets: [{{
        label: '{y_label}',
        data: {y_js},
        borderColor: '{color}',
        borderWidth: 2,
        pointRadius: 0,
        fill: true,
        backgroundColor: '{color}22',
        tension: 0.4
      }}]
    }},
    options: {{
      animation: false,
      responsive: true,
      plugins: {{
        legend: {{ display: false }},
        tooltip: {{
          backgroundColor: '#0a0e1a',
          borderColor: '{color}',
          borderWidth: 1,
          titleColor: '#f59e0b',
          bodyColor: '#94a3b8',
          callbacks: {{
            title: (items) => '{x_label} = ' + parseFloat(items[0].label).toFixed(2),
            label: (item) => '{y_label} = ' + item.raw.toFixed(6)
          }}
        }}
      }},
      scales: {{
        x: {{
          ticks: {{ color:'#64748b', maxTicksLimit:8, callback: v => parseFloat(v).toFixed(1) }},
          grid: {{ color:'#1e2a45' }},
          title: {{ display:true, text:'{x_label}', color:'#64748b' }}
        }},
        y: {{
          ticks: {{ color:'#64748b', maxTicksLimit:6 }},
          grid: {{ color:'#1e2a45' }},
          title: {{ display:true, text:'{y_label}', color:'#64748b' }}
        }}
      }}
    }}
  }});
}})();
</script>
"""


# ── main show() ──────────────────────────────────────────────────────────────

def show():
    page_header("📈", "Analisis Reliability", "Fungsi R(t), F(t), f(t), h(t) dan MTTF/MTTR")

    # ── Step 1: ambil parameter ──────────────────────────────────────────────
    step_badge(1, "Parameter Distribusi")

    mod2 = st.session_state.get("mod2_result")
    mod1 = st.session_state.get("mod1_result")

    # Tentukan distribusi & parameter dari hasil GoF
    dist_auto, params_auto = None, {}
    if mod2 and mod1:
        dist_auto = mod2.get("distribusi")
        r = mod1.get("results", {}).get(dist_auto, {})
        a = r.get("a", 0)
        b = r.get("b", 1)
        if dist_auto == "Weibull":
            params_auto = {"beta": round(b, 6), "eta": round(math.exp(-a / b), 6)}
        elif dist_auto == "Eksponensial":
            params_auto = {"lambda": round(b, 6)}
        elif dist_auto in ("Normal", "Lognormal"):
            params_auto = {"mu": round(-a / b, 6), "sigma": round(1 / b, 6)}

    source = st.radio(
        "Sumber parameter:",
        ["Otomatis dari hasil GoF", "Input manual"],
        horizontal=True,
        label_visibility="collapsed",
    )

    if source == "Otomatis dari hasil GoF":
        if not dist_auto:
            st.warning("⚠️ Belum ada hasil GoF. Jalankan Modul 3 & 4 terlebih dahulu, atau pilih Input Manual.")
            return
        dist = dist_auto
        params = params_auto
        dtype = st.session_state.get("mod1_dtype", "TTF")
        mesin = st.session_state.get("mod1_mesin", "—")

        st.markdown(f"""
        <div style="background:#0f1628;border:1px solid #1e2a45;border-radius:8px;
                    padding:14px 18px;margin:12px 0;font-family:'IBM Plex Mono',monospace;font-size:13px;">
          <span style="color:#64748b;">Mesin:</span>
          <span style="color:#f8fafc;margin-left:8px;">{mesin}</span>
          &nbsp;&nbsp;
          <span style="color:#64748b;">Distribusi:</span>
          <span style="color:#f59e0b;margin-left:8px;font-weight:700;">{dist}</span>
          &nbsp;&nbsp;
          <span style="color:#64748b;">Tipe Data:</span>
          <span style="color:#f8fafc;margin-left:8px;">{dtype}</span>
        </div>
        """, unsafe_allow_html=True)

        # tampilkan parameter
        param_str = "  |  ".join([f"<span style='color:#64748b'>{k}</span> = <span style='color:#38bdf8'>{v}</span>" for k, v in params.items()])
        st.markdown(f"<p style='font-family:IBM Plex Mono,monospace;font-size:13px;'>{param_str}</p>", unsafe_allow_html=True)

    else:
        # Input manual
        col1, col2 = st.columns([1, 2])
        with col1:
            dist = st.selectbox("Distribusi", ["Weibull", "Eksponensial", "Normal", "Lognormal"])
            dtype = st.radio("Tipe Data", ["TTF", "TTR"], horizontal=True)

        with col2:
            params = {}
            if dist == "Weibull":
                c1, c2 = st.columns(2)
                params["beta"] = c1.number_input("β (shape)", value=1.5, min_value=0.01, format="%.4f")
                params["eta"] = c2.number_input("η (scale)", value=200.0, min_value=0.01, format="%.4f")
            elif dist == "Eksponensial":
                params["lambda"] = st.number_input("λ (failure rate)", value=0.005, min_value=1e-10, format="%.6f")
            elif dist in ("Normal", "Lognormal"):
                c1, c2 = st.columns(2)
                lbl_mu = "μ" if dist == "Normal" else "μ (ln-scale)"
                lbl_sigma = "σ" if dist == "Normal" else "σ (ln-scale)"
                params["mu"] = c1.number_input(lbl_mu, value=100.0, format="%.4f")
                params["sigma"] = c2.number_input(lbl_sigma, value=20.0, min_value=0.001, format="%.4f")

    st.markdown("<hr style='border-color:#1e2a45;margin:20px 0'>", unsafe_allow_html=True)

    # ── Step 2: grafik ──────────────────────────────────────────────────────
    step_badge(2, "Grafik Fungsi Reliability")

    t_range = _build_t_range(params, dist)
    R_vals = [compute_reliability(dist, params, t)["R"] for t in t_range]
    F_vals = [compute_reliability(dist, params, t)["F"] for t in t_range]
    f_vals = [compute_reliability(dist, params, t)["f"] for t in t_range]
    h_vals = [compute_reliability(dist, params, t)["h"] for t in t_range]

    # Render grafik dalam 2 kolom
    col_l, col_r = st.columns(2)

    chart_script = '<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>'

    with col_l:
        st.components.v1.html(
            chart_script + _line_chart_html("R(t) — Reliability Function", t_range, R_vals, "#22c55e", "R(t)"),
            height=260,
        )
        st.components.v1.html(
            _line_chart_html("f(t) — Probability Density Function", t_range, f_vals, "#38bdf8", "f(t)"),
            height=260,
        )

    with col_r:
        st.components.v1.html(
            chart_script + _line_chart_html("F(t) — Cumulative Distribution Function", t_range, F_vals, "#f97316", "F(t)"),
            height=260,
        )
        st.components.v1.html(
            chart_script + _line_chart_html("h(t) — Hazard Rate Function", t_range, h_vals, "#e879f9", "h(t)"),
            height=260,
        )

    st.markdown("<hr style='border-color:#1e2a45;margin:20px 0'>", unsafe_allow_html=True)

    # ── Step 3: MTTF/MTTR ───────────────────────────────────────────────────
    step_badge(3, "MTTF / MTTR")

    mttf = compute_mttf(dist, params)
    label_mttf = "MTTR" if (source == "Otomatis dari hasil GoF" and st.session_state.get("mod1_dtype") == "TTR") else "MTTF"

    st.markdown(f"""
    <div style="background:#0f1628;border:1px solid #f59e0b44;border-radius:8px;
                padding:20px 24px;display:inline-block;margin-bottom:16px;">
      <p style="color:#64748b;font-family:'IBM Plex Mono',monospace;font-size:12px;
                margin:0 0 4px 0;letter-spacing:2px;text-transform:uppercase;">{label_mttf}</p>
      <p style="color:#f59e0b;font-family:'IBM Plex Mono',monospace;font-size:32px;
                font-weight:700;margin:0;">{r2(mttf)}</p>
      <p style="color:#64748b;font-family:'IBM Plex Mono',monospace;font-size:11px;margin:4px 0 0 0;">
        satuan waktu
      </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("<hr style='border-color:#1e2a45;margin:20px 0'>", unsafe_allow_html=True)

    # ── Step 4: Point Estimate ───────────────────────────────────────────────
    step_badge(4, "Point Estimate pada t tertentu")

    col_input, col_spacer = st.columns([1, 3])
    with col_input:
        t_input = st.number_input("Masukkan nilai t:", min_value=0.001, value=float(r2(mttf)), format="%.3f")

    res = compute_reliability(dist, params, t_input)
    if res:
        cols = st.columns(4)
        metrics = [
            ("R(t)", res["R"], "#22c55e", "Probabilitas masih beroperasi"),
            ("F(t)", res["F"], "#f97316", "Probabilitas sudah gagal"),
            ("f(t)", res["f"], "#38bdf8", "Probability density"),
            ("h(t)", res["h"], "#e879f9", "Laju kegagalan sesaat"),
        ]
        for col, (label, val, color, desc) in zip(cols, metrics):
            with col:
                st.markdown(f"""
                <div style="background:#0f1628;border:1px solid {color}44;border-radius:8px;
                            padding:16px;text-align:center;">
                  <p style="color:#64748b;font-family:'IBM Plex Mono',monospace;
                            font-size:11px;margin:0 0 6px 0;letter-spacing:1px;">{label}</p>
                  <p style="color:{color};font-family:'IBM Plex Mono',monospace;
                            font-size:22px;font-weight:700;margin:0;">{val:.6f}</p>
                  <p style="color:#475569;font-family:'IBM Plex Sans',sans-serif;
                            font-size:10px;margin:6px 0 0 0;">{desc}</p>
                </div>
                """, unsafe_allow_html=True)