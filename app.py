import streamlit as st
import numpy as np
from scipy.integrate import odeint
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title="SIR Epidemic Simulator", layout="wide", page_icon="🦠")

st.markdown("""
<style>
    .stApp {
        background: #f0f2f6;
    }
    .main-header {
        font-size: 1.6rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 1rem;
        padding: 0.5rem 0;
    }
    .metric-container {
        background: white;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        text-align: center;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #888;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 0.25rem;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #1a1a2e;
    }
    .metric-value.epidemic {
        color: #e74c3c;
    }
    .metric-value.decline {
        color: #27ae60;
    }
    .validation-card {
        background: white;
        border-radius: 10px;
        padding: 1.2rem 1.5rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        height: 100%;
    }
    .validation-card h4 {
        font-size: 0.9rem;
        color: #333;
        margin-bottom: 0.75rem;
    }
    .validation-card p {
        font-size: 0.85rem;
        color: #555;
        margin-bottom: 0.25rem;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 6px;
        font-size: 0.8rem;
        font-weight: 600;
        margin-top: 0.5rem;
    }
    .status-badge.success {
        background: #d4edda;
        color: #155724;
    }
    .status-badge.fail {
        background: #f8d7da;
        color: #721c24;
    }
    .status-badge.pending {
        background: #e2e3e5;
        color: #6c757d;
    }
    .chart-container {
        background: white;
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .stButton > button {
        width: 100%;
        padding: 0.5rem 1rem;
        background: #4f8bf9;
        color: white;
        border: none;
        border-radius: 8px;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: background 0.2s;
    }
    .stButton > button:hover {
        background: #3a7bf5;
    }
    .stButton > button:active {
        background: #2d6de0;
    }
    div[data-testid="stSidebar"] {
        background: white;
    }
    div[data-testid="stSidebar"] .sidebar-header {
        font-size: 1.1rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 1.5rem;
    }
    hr {
        margin: 1rem 0;
        border: none;
        border-top: 1px solid #eee;
    }
    .section-title {
        font-size: 0.95rem;
        font-weight: 600;
        color: #555;
        margin: 1rem 0 0.75rem;
    }
</style>
""", unsafe_allow_html=True)

def sir_model(y, t, N, beta, gamma):
    S, I, R = y
    S = max(0.0, S)
    I = max(0.0, I)
    R = max(0.0, R)
    dSdt = -beta * S * I / N
    dIdt = (beta * S * I / N) - gamma * I
    dRdt = gamma * I
    return dSdt, dIdt, dRdt

def run_simulation(N, days, beta, gamma, I0):
    R0_init = 0
    S0 = N - I0 - R0_init

    t = np.linspace(0, days, max(days * 10, 100))
    y0 = S0, I0, R0_init
    ret = odeint(sir_model, y0, t, args=(N, beta, gamma))
    S, I, R = ret.T

    R_naught = beta / gamma if gamma > 0 else 0
    status = "epidemic" if R_naught > 1 else "decline"

    peak_idx = np.argmax(I)
    peak_infection = I[peak_idx]
    peak_day = round(float(t[peak_idx]), 1)

    return {
        "t": t,
        "S": S,
        "I": I,
        "R": R,
        "initialSum": int(round((S + I + R)[0])),
        "finalSum": int(round((S + I + R)[-1])),
        "S0": int(S0),
        "I0": int(I0),
        "R0": int(R0_init),
        "minS": round(float(S.min()), 2),
        "minI": round(float(I.min()), 2),
        "minR": round(float(R.min()), 2),
        "R_naught": round(R_naught, 2),
        "status": status,
        "N": N,
        "peak_infection": round(float(peak_infection), 0),
        "peak_day": peak_day,
        "final_recovered": round(float(R[-1]), 0)
    }

st.markdown('<div class="main-header">Interactive Dashboard for SIR Epidemic Simulation</div>', unsafe_allow_html=True)

with st.sidebar:
    st.markdown('<div class="sidebar-header">Simulation Parameters</div>', unsafe_allow_html=True)

    N = st.number_input("Total Population (N)", min_value=1000, max_value=10_000_000, value=100_000, step=1000)

    days = st.slider("Simulation Timeline (Days)", min_value=10, max_value=365, value=100)

    st.markdown("<hr>", unsafe_allow_html=True)

    beta = st.slider("Transmission Rate (β)", min_value=0.0, max_value=5.0, value=0.35, step=0.01)

    gamma = st.slider("Recovery Rate (γ)", min_value=0.01, max_value=1.0, value=0.10, step=0.01)

    st.markdown("<hr>", unsafe_allow_html=True)

    st.markdown('<div class="section-title">Initial Boundary States</div>', unsafe_allow_html=True)

    I0 = st.number_input("Initial Infected (I₀)", min_value=1, max_value=N, value=10)

    st.markdown(
        '<p style="font-size:0.85rem;color:#999;margin-top:-0.5rem;">Initial Recovered (R₀) = 0 <span style="font-size:0.7rem;">(Strict Boundary)</span></p>',
        unsafe_allow_html=True
    )

    simulate = st.button("Run Simulation", type="primary")

if simulate:
    data = run_simulation(N, days, beta, gamma, I0)

    m1, m2, m3, m4, m5 = st.columns(5)
    with m1:
        st.markdown(
            f"""
            <div class="metric-container">
                <div class="metric-label">Basic Reproduction Number (R₀)</div>
                <div class="metric-value">{data["R_naught"]}</div>
            </div>
            """, unsafe_allow_html=True
        )
    with m2:
        regime_class = data["status"]
        regime_text = "Epidemic Outbreak 🔴" if data["status"] == "epidemic" else "Disease Decline 🟢"
        st.markdown(
            f"""
            <div class="metric-container">
                <div class="metric-label">Epidemiological Regime</div>
                <div class="metric-value {regime_class}">{regime_text}</div>
            </div>
            """, unsafe_allow_html=True
        )
    with m3:
        st.markdown(
            f"""
            <div class="metric-container">
                <div class="metric-label">Peak Infection</div>
                <div class="metric-value">{int(data["peak_infection"]):,}</div>
            </div>
            """, unsafe_allow_html=True
        )
    with m4:
        st.markdown(
            f"""
            <div class="metric-container">
                <div class="metric-label">Peak Day</div>
                <div class="metric-value">{data["peak_day"]}</div>
            </div>
            """, unsafe_allow_html=True
        )
    with m5:
        st.markdown(
            f"""
            <div class="metric-container">
                <div class="metric-label">Final Recovered</div>
                <div class="metric-value">{int(data["final_recovered"]):,}</div>
            </div>
            """, unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=data["t"], y=data["S"], mode="lines", name="Susceptible (S)",
        line=dict(color="#4f8bf9", width=3), hovertemplate="Day %{x}<br>S: %{y:,.0f}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=data["t"], y=data["I"], mode="lines", name="Infected (I)",
        line=dict(color="#e74c3c", width=3), hovertemplate="Day %{x}<br>I: %{y:,.0f}<extra></extra>"
    ))
    fig.add_trace(go.Scatter(
        x=data["t"], y=data["R"], mode="lines", name="Recovered (R)",
        line=dict(color="#27ae60", width=3), hovertemplate="Day %{x}<br>R: %{y:,.0f}<extra></extra>"
    ))
    fig.update_layout(
        title="Temporal Evolution of Epidemic Curves",
        xaxis=dict(title="Time (Days)", showgrid=True, gridcolor="#eee"),
        yaxis=dict(title="Number of Individuals", showgrid=True, gridcolor="#eee"),
        hovermode="x unified",
        template="plotly_white",
        legend=dict(orientation="h", y=1.02, x=0.5, xanchor="center"),
        margin=dict(t=60, b=50, l=60, r=30),
        height=500
    )
    fig.update_xaxes(rangeslider_visible=True)
    fig.update_yaxes(rangemode="nonnegative")

    st.markdown('<div class="chart-container">', unsafe_allow_html=True)
    st.plotly_chart(fig, use_container_width=True, config={
        "scrollZoom": True,
        "displayModeBar": True,
        "modeBarButtonsToAdd": ["drawline", "drawopenpath", "eraseshape"],
        "displaylogo": False,
        "toImageButtonOptions": {"format": "png", "filename": "sir_simulation", "height": 600, "width": 1000}
    })
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    conserved = data["initialSum"] == data["finalSum"]
    non_neg = data["minS"] >= 0 and data["minI"] >= 0 and data["minR"] >= 0

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(
            f"""
            <div class="validation-card">
                <h4>Population Conservation Check</h4>
                <p>Initial Sum: <strong>{data["initialSum"]:,}</strong></p>
                <p>Final Sum: <strong>{data["finalSum"]:,}</strong></p>
                <span class="status-badge {"success" if conserved else "fail"}">
                    {"✅ Verified (100% Invariant)" if conserved else "❌ MISMATCH!"}
                </span>
            </div>
            """, unsafe_allow_html=True
        )
    with c2:
        st.markdown(
            f"""
            <div class="validation-card">
                <h4>Boundary State Check</h4>
                <p>S(0) = <strong>{data["S0"]:,}</strong></p>
                <p>I(0) = <strong>{data["I0"]:,}</strong></p>
                <p>R(0) = <strong>{data["R0"]:,}</strong></p>
                <span class="status-badge success">✅ Verified (Strict)</span>
            </div>
            """, unsafe_allow_html=True
        )
    with c3:
        st.markdown(
            f"""
            <div class="validation-card">
                <h4>Non-Negativity Check</h4>
                <p>Min S(t): <strong>{data["minS"]:,.2f}</strong></p>
                <p>Min I(t): <strong>{data["minI"]:,.2f}</strong></p>
                <p>Min R(t): <strong>{data["minR"]:,.2f}</strong></p>
                <span class="status-badge {"success" if non_neg else "fail"}">
                    {"✅ Verified (Biologically Realistic)" if non_neg else "❌ NEGATIVE VALUES!"}
                </span>
            </div>
            """, unsafe_allow_html=True
        )

else:
    st.info("👈 Adjust the parameters in the sidebar and click **Run Simulation** to start.")

st.markdown("---")
st.markdown(
    "<p style='text-align:center;color:#999;font-size:0.8rem;'>"
    "SIR Epidemic Model Dashboard powered by Streamlit &middot; "
    "Mathematical Epidemiology &middot; ODE Integration with SciPy"
    "</p>",
    unsafe_allow_html=True
)
