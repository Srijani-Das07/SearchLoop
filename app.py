import streamlit as st
import os
import time
from src.agent import run_research_agent

st.set_page_config(
    page_title="SearchLoop",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── Custom CSS ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=DM+Mono:wght@300;400;500&display=swap');

/* Base */
html, body, [class*="css"] {
    font-family: 'DM Mono', monospace;
    background-color: #0a0a0a;
    color: #e8e8e8;
}

/* Hide default streamlit elements */
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 2.5rem 3rem 2rem 3rem; max-width: 1400px; }

/* Hero title */
.hero-title {
    font-family: 'Syne', sans-serif;
    font-size: 3.2rem;
    font-weight: 800;
    letter-spacing: -0.03em;
    background: linear-gradient(135deg, #ffffff 0%, #a0a0a0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    line-height: 1.1;
    margin-bottom: 0.3rem;
}

.hero-sub {
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    color: #555;
    letter-spacing: 0.08em;
    text-transform: uppercase;
    margin-bottom: 2.5rem;
}

/* Input */
.stTextInput > div > div > input {
    background: #111 !important;
    border: 1px solid #222 !important;
    border-radius: 6px !important;
    color: #e8e8e8 !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.9rem !important;
    padding: 0.75rem 1rem !important;
    transition: border-color 0.2s;
}
.stTextInput > div > div > input:focus {
    border-color: #3a3a3a !important;
    box-shadow: none !important;
}
.stTextInput label {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.72rem !important;
    text-transform: uppercase !important;
    letter-spacing: 0.1em !important;
    color: #555 !important;
}

/* Button */
.stButton > button {
    background: #e8e8e8 !important;
    color: #0a0a0a !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Syne', sans-serif !important;
    font-weight: 700 !important;
    font-size: 0.85rem !important;
    letter-spacing: 0.05em !important;
    padding: 0.6rem 2rem !important;
    transition: all 0.2s !important;
    text-transform: uppercase !important;
}
.stButton > button:hover {
    background: #ffffff !important;
    transform: translateY(-1px);
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: #0d0d0d !important;
    border-right: 1px solid #1a1a1a !important;
}
[data-testid="stSidebar"] * {
    font-family: 'DM Mono', monospace !important;
}
[data-testid="stSidebar"] .stTextInput > div > div > input {
    font-size: 0.78rem !important;
}

/* Sidebar header */
.sidebar-brand {
    font-family: 'Syne', sans-serif;
    font-size: 1.1rem;
    font-weight: 700;
    color: #e8e8e8;
    margin-bottom: 1.5rem;
    padding-bottom: 1rem;
    border-bottom: 1px solid #1a1a1a;
}

/* Agent log panel */
.log-panel {
    background: #0d0d0d;
    border: 1px solid #1a1a1a;
    border-radius: 8px;
    padding: 1.2rem 1.4rem;
    min-height: 200px;
    font-family: 'DM Mono', monospace;
    font-size: 0.78rem;
    line-height: 1.9;
    color: #666;
}

/* Section labels */
.section-label {
    font-family: 'DM Mono', monospace;
    font-size: 0.68rem;
    text-transform: uppercase;
    letter-spacing: 0.15em;
    color: #444;
    margin-bottom: 0.8rem;
}

/* Report card */
.report-title {
    font-family: 'Syne', sans-serif;
    font-size: 1.6rem;
    font-weight: 700;
    color: #e8e8e8;
    margin-bottom: 0.5rem;
    line-height: 1.3;
}

.report-summary {
    background: #111;
    border-left: 2px solid #333;
    padding: 1rem 1.2rem;
    font-size: 0.85rem;
    color: #aaa;
    line-height: 1.7;
    border-radius: 0 6px 6px 0;
    margin-bottom: 1.5rem;
}

.report-section-heading {
    font-family: 'Syne', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    color: #ccc;
    margin-top: 1.5rem;
    margin-bottom: 0.5rem;
    padding-bottom: 0.4rem;
    border-bottom: 1px solid #1a1a1a;
}

.finding-item {
    font-size: 0.82rem;
    color: #999;
    padding: 0.4rem 0;
    padding-left: 1rem;
    border-left: 1px solid #2a2a2a;
    margin-bottom: 0.4rem;
    line-height: 1.6;
}

/* Divider */
hr {
    border-color: #1a1a1a !important;
    margin: 1.5rem 0 !important;
}

/* Alerts */
.stAlert {
    border-radius: 6px !important;
    font-family: 'DM Mono', monospace !important;
    font-size: 0.8rem !important;
}

/* Spinner */
.stSpinner > div {
    border-top-color: #e8e8e8 !important;
}

/* Expander */
.streamlit-expanderHeader {
    font-family: 'DM Mono', monospace !important;
    font-size: 0.78rem !important;
    color: #555 !important;
}
</style>
""", unsafe_allow_html=True)

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-brand">⟳ SearchLoop</div>', unsafe_allow_html=True)
    st.markdown('<div class="section-label">API Keys</div>', unsafe_allow_html=True)
    gemini_key = st.text_input("Gemini API Key", type="password", value=os.getenv("GEMINI_API_KEY", ""), label_visibility="collapsed", placeholder="Gemini API Key")
    tavily_key = st.text_input("Tavily API Key", type="password", value=os.getenv("TAVILY_API_KEY", ""), label_visibility="collapsed", placeholder="Tavily API Key")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">Get free keys</div>', unsafe_allow_html=True)
    st.markdown("→ [Gemini API](https://aistudio.google.com) — Google AI Studio")
    st.markdown("→ [Tavily](https://tavily.com) — Search API")

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-label">How it works</div>', unsafe_allow_html=True)
    st.markdown("""
<div style="font-size:0.78rem; color:#555; line-height:2;">
01 — Receive query<br>
02 — Decompose into sub-questions<br>
03 — Search web iteratively<br>
04 — Evaluate coverage<br>
05 — Loop back if needed<br>
06 — Synthesize report
</div>
""", unsafe_allow_html=True)

# ── Main ─────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">SearchLoop</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Autonomous Research Agent · Tool-calling loops · Structured reports</div>', unsafe_allow_html=True)

query = st.text_input(
    "query",
    placeholder="e.g. What are the latest advances in vision transformers for medical imaging?",
    label_visibility="collapsed"
)

run_button = st.button("→ Run Research")

if run_button:
    if not gemini_key or not tavily_key:
        st.error("Please enter both API keys in the sidebar.")
        st.stop()
    if not query.strip():
        st.error("Please enter a research query.")
        st.stop()

    st.markdown("<hr>", unsafe_allow_html=True)
    col_log, col_report = st.columns([1, 2], gap="large")

    with col_log:
        st.markdown('<div class="section-label">Agent Activity</div>', unsafe_allow_html=True)
        log_placeholder = st.empty()
        log_placeholder.markdown('<div class="log-panel">Initializing agent...</div>', unsafe_allow_html=True)

    with col_report:
        st.markdown('<div class="section-label">Research Report</div>', unsafe_allow_html=True)
        report_placeholder = st.empty()
        report_placeholder.markdown('<div class="log-panel" style="color:#333;">Waiting for agent to complete research...</div>', unsafe_allow_html=True)

    try:
        with st.spinner(""):
            start = time.time()
            result = run_research_agent(query, gemini_key, tavily_key)
            elapsed = round(time.time() - start, 1)

        # Update log
        log_html = '<div class="log-panel">' + "<br>".join(result["search_log"]) + f'<br><br><span style="color:#333;">── {elapsed}s · {result["iterations"]} iterations</span></div>'
        log_placeholder.markdown(log_html, unsafe_allow_html=True)

        report = result.get("report")
        if report:
            report_placeholder.empty()
            with col_report:
                st.markdown(f'<div class="report-title">{report["title"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="report-summary">{report["summary"]}</div>', unsafe_allow_html=True)

                for section in report.get("sections", []):
                    st.markdown(f'<div class="report-section-heading">{section["heading"]}</div>', unsafe_allow_html=True)
                    st.markdown(f'<div style="font-size:0.83rem; color:#888; line-height:1.8;">{section["content"]}</div>', unsafe_allow_html=True)

                st.markdown('<div class="report-section-heading">Key Findings</div>', unsafe_allow_html=True)
                for finding in report.get("key_findings", []):
                    st.markdown(f'<div class="finding-item">→ {finding}</div>', unsafe_allow_html=True)

                if report.get("sources"):
                    with st.expander("Sources"):
                        for src in report["sources"]:
                            st.markdown(f'<div style="font-size:0.75rem; color:#444;">{src}</div>', unsafe_allow_html=True)
        else:
            report_placeholder.error("Agent did not produce a report. Try a more specific query.")

    except Exception as e:
        err = str(e)
        if "429" in err or "quota" in err.lower() or "ResourceExhausted" in err:
            st.error("Rate limit hit. You've exceeded your free tier quota. Wait a minute and try again, or check your Gemini API limits at ai.dev/rate-limit.")
        elif "API_KEY_INVALID" in err or "invalid" in err.lower():
            st.error("Invalid API key. Please double-check your Gemini or Tavily key in the sidebar.")
        elif "tavily" in err.lower():
            st.error("Tavily search failed. Please check your Tavily API key.")
        else:
            st.error(f"Something went wrong: {err}")
            