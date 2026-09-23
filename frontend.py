
from typing import Any, Dict

import streamlit as st

from backend import workflow


st.set_page_config(
    page_title="Portfolio Intelligence Console",
    page_icon="PI",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
    :root {
        --ink: #14213d;
        --muted: #60708f;
        --line: #dce4ef;
        --paper: #f5f8fc;
        --blue: #2563eb;
        --green: #138a72;
        --amber: #b7791f;
    }

    .stApp {
        background: linear-gradient(135deg, #f7faff 0%, #eef4fb 48%, #f8fafc 100%);
        color: var(--ink);
    }

    [data-testid="stSidebar"] {
        background: #14213d;
    }

    [data-testid="stSidebar"] * {
        color: #eef4ff;
    }

    .eyebrow {
        color: var(--blue);
        font-size: 0.75rem;
        font-weight: 800;
        letter-spacing: 0.12em;
        text-transform: uppercase;
        margin-bottom: 0.35rem;
    }

    .hero {
        border-bottom: 1px solid var(--line);
        margin-bottom: 1.5rem;
        padding: 1.5rem 0 1.25rem;
    }

    .hero h1 {
        color: var(--ink);
        font-size: clamp(2rem, 4vw, 3.4rem);
        letter-spacing: -0.04em;
        line-height: 1;
        margin: 0;
    }

    .hero p {
        color: var(--muted);
        font-size: 1.05rem;
        margin: 0.8rem 0 0;
        max-width: 48rem;
    }

    .section-label {
        color: var(--ink);
        font-size: 1.05rem;
        font-weight: 750;
        margin: 1rem 0 0.7rem;
    }

    .metric-card {
        background: rgba(255, 255, 255, 0.76);
        border: 1px solid var(--line);
        border-radius: 8px;
        padding: 1rem;
        min-height: 6rem;
    }

    .metric-label {
        color: var(--muted);
        font-size: 0.76rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
    }

    .metric-value {
        color: var(--ink);
        font-size: 1.65rem;
        font-weight: 800;
        margin-top: 0.35rem;
    }

    .agent-strip {
        background: #ffffff;
        border-left: 4px solid var(--blue);
        border-radius: 6px;
        box-shadow: 0 5px 18px rgba(20, 33, 61, 0.06);
        margin-bottom: 0.65rem;
        padding: 0.8rem 1rem;
    }

    .agent-name {
        color: var(--ink);
        font-weight: 750;
    }

    .agent-state {
        color: var(--green);
        float: right;
        font-size: 0.78rem;
        font-weight: 800;
        text-transform: uppercase;
    }
    
    .stTextArea {
        color: #FFFFFF !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def initial_state(query: str) -> Dict[str, Any]:
    """Build the state expected by the existing graph."""
    return {
        "raw_query": query,
        "target_tickers": [],
        "market_data": {},
        "risk_metrics": {},
        "compliance_passed": False,
        "audit_trail": [],
        "final_report": "",
    }


def render_metric(label: str, value: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_result(result: Dict[str, Any]) -> None:
    tickers = result.get("target_tickers", [])
    market_data = result.get("market_data", {})
    risk_metrics = result.get("risk_metrics", {})
    compliance_passed = result.get("compliance_passed", False)

    st.markdown('<div class="section-label">Execution snapshot</div>', unsafe_allow_html=True)
    summary_columns = st.columns(4)
    with summary_columns[0]:
        render_metric("Agents completed", str(len(result.get("audit_trail", []))))
    with summary_columns[1]:
        render_metric("Assets detected", str(len(tickers)))
    with summary_columns[2]:
        render_metric("Risk models", str(len(risk_metrics)))
    with summary_columns[3]:
        render_metric("Publication status", "Approved" if compliance_passed else "Review")

    left, right = st.columns([1.15, 0.85])
    with left:
        st.markdown('<div class="section-label">Market and risk data</div>', unsafe_allow_html=True)
        if market_data:
            for ticker, values in market_data.items():
                risk = risk_metrics.get(ticker, {})
                st.markdown(f"**{ticker}**")
                st.dataframe(
                    {
                        "Current price": [values.get("current_price")],
                        "P/E ratio": [values.get("pe_ratio")],
                        "Calculated volatility": [risk.get("calculated_volatility")],
                    },
                    hide_index=True,
                    width="stretch",
                )
        else:
            st.info("The workflow returned no market data.")

    with right:
        st.markdown('<div class="section-label">Final report</div>', unsafe_allow_html=True)
        if compliance_passed:
            st.success("Publication approved")
        else:
            st.warning("Compliance review required")
        st.write(result.get("final_report", "No report returned."))

        st.markdown('<div class="section-label">Audit trail</div>', unsafe_allow_html=True)
        for index, event in enumerate(result.get("audit_trail", []), start=1):
            st.markdown(
                f'<div class="agent-strip"><span class="agent-name">Step {index}</span>'
                f'<span class="agent-state">Complete</span><br>{event}</div>',
                unsafe_allow_html=True,
            )


st.markdown(
    """
    <div class="hero">
        <div class="eyebrow">Multi-agent financial analysis</div>
        <h1>Portfolio Intelligence Console</h1>
        <p>Send one investment question through the existing orchestration graph and inspect each result as it returns.</p>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### Pipeline")
    for agent in ("Orchestrator", "Market ingestion", "Quantitative risk", "Compliance XAI"):
        st.markdown(f"- {agent}")
    st.divider()
    st.caption("The workflow uses the configured Google model and market data providers from the existing backend.")

query = st.text_area(
    "Analysis request",
    value="Check recent volatility metrics and compliance exposure risks for AAPL and GOOG.",
    height=120,
    help="Describe the portfolio question and include the ticker symbols you want analyzed.",
)

run_analysis = st.button("Run orchestration", type="primary")

if run_analysis:
    if not query.strip():
        st.error("Enter an analysis request before starting the workflow.")
    else:
        with st.status("Running agent orchestration...", expanded=True) as status:
            try:
                st.write("Initializing the existing LangGraph workflow.")
                result = workflow.invoke(initial_state(query.strip()))
                st.session_state["latest_result"] = result
                status.update(label="Orchestration complete", state="complete", expanded=False)
            except Exception as error:
                status.update(label="Orchestration failed", state="error")
                st.error(f"The existing workflow could not complete: {error}")

if "latest_result" in st.session_state:
    render_result(st.session_state["latest_result"])
else:
    st.info("Enter a request and run the orchestration to view agent output.")
