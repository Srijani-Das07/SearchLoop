import streamlit as st
import os
import time
from src.agent import run_research_agent

st.set_page_config(
    page_title="SearchLoop",
    page_icon="🔬",
    layout="wide"
)

st.title("SearchLoop")
st.caption("An autonomous research agent that self-directs multi-step web research using tool-calling loops.")

with st.sidebar:
    st.header("⚙️ Configuration")
    gemini_key = st.text_input("Gemini API Key", type="password", value=os.getenv("GEMINI_API_KEY", ""))
    tavily_key = st.text_input("Tavily API Key", type="password", value=os.getenv("TAVILY_API_KEY", ""))
    st.divider()
    st.markdown("**Get free API keys:**")
    st.markdown("- [Gemini API](https://aistudio.google.com) — Google AI Studio")
    st.markdown("- [Tavily](https://tavily.com) — Search API")
    st.divider()
    st.markdown("**How it works:**")
    st.markdown("""
    1. Agent receives your query
    2. Breaks it into sub-questions
    3. Searches the web iteratively
    4. Evaluates if information is sufficient
    5. Loops back if needed
    6. Synthesizes a structured report
    """)

query = st.text_input(
    "Research Query",
    placeholder="e.g. What are the latest advances in vision transformers for medical imaging?",
)

run_button = st.button("Research", type="primary")

if run_button:
    if not gemini_key or not tavily_key:
        st.error("⚠️ Please enter both API keys in the sidebar.")
        st.stop()

    if not query.strip():
        st.error("⚠️ Please enter a research query.")
        st.stop()

    st.divider()
    col_log, col_report = st.columns([1, 2])

    with col_log:
        st.subheader("🤖 Agent Activity")
        log_container = st.empty()

    with col_report:
        st.subheader("📄 Research Report")
        report_container = st.empty()
        report_container.info("Agent is researching... this takes 30–60 seconds.")

    try:
        with st.spinner("Agent working..."):
            start = time.time()
            result = run_research_agent(query, gemini_key, tavily_key)
            elapsed = round(time.time() - start, 1)

        log_container.markdown("\n\n".join(result["search_log"]))
        st.caption(f"Completed in {elapsed}s · {result['iterations']} iteration(s)")

        report = result.get("report")
        if report:
            report_container.empty()
            with col_report:
                st.markdown(f"## {report['title']}")
                st.info(report["summary"])

                for section in report.get("sections", []):
                    st.markdown(f"### {section['heading']}")
                    st.markdown(section["content"])

                st.markdown("### 🔑 Key Findings")
                for finding in report.get("key_findings", []):
                    st.markdown(f"- {finding}")

                if report.get("sources"):
                    with st.expander("📚 Sources"):
                        for src in report["sources"]:
                            st.markdown(f"- {src}")
        else:
            report_container.error("Agent did not produce a report. Try a more specific query.")

    except Exception as e:
        err = str(e)
        if "429" in err or "quota" in err.lower() or "ResourceExhausted" in err:
            st.error("⚠️ Rate limit hit. You've exceeded your free tier quota. Wait a minute and try again, or check your Gemini API limits at [ai.dev/rate-limit](https://ai.dev/rate-limit).")
        elif "API_KEY_INVALID" in err or "invalid" in err.lower():
            st.error("⚠️ Invalid API key. Please double-check your Gemini or Tavily key in the sidebar.")
        elif "TAVILY" in err.upper() or "tavily" in err.lower():
            st.error("⚠️ Tavily search failed. Please check your Tavily API key.")
        else:
            st.error(f"⚠️ Something went wrong: {err}")
            