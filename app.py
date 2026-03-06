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
st.caption("An LLM-powered agent that self-directs multi-step web research using tool-calling loops.")

with st.sidebar:
    st.header("⚙️ Configuration")
    gemini_key = st.text_input("Gemini API Key", type="password", value=os.getenv("GEMINI_API_KEY", ""))
    tavily_key = st.text_input("Tavily API Key", type="password", value=os.getenv("TAVILY_API_KEY", ""))
    st.divider()
    st.markdown("**How it works:**")
    st.markdown("""
    1. Agent receives your query
    2. Breaks it into sub-questions
    3. Searches the web iteratively
    4. Evaluates if info is sufficient
    5. Loops back if needed
    6. Synthesizes a structured report
    """)

query = st.text_input(
    "Research Query",
    placeholder="e.g. What are the latest advances in vision transformers for medical imaging?",
    label_visibility="visible"
)

col1, col2 = st.columns([1, 5])
with col1:
    run_button = st.button("🚀 Research", type="primary", use_container_width=True)

if run_button:
    if not gemini_key or not tavily_key:
        st.error("Please enter both API keys in the sidebar.")
    elif not query.strip():
        st.error("Please enter a research query.")
    else:
        st.divider()
        col_log, col_report = st.columns([1, 2])

        with col_log:
            st.subheader("🤖 Agent Activity")
            log_container = st.empty()

        with col_report:
            st.subheader("📄 Research Report")
            report_container = st.empty()
            report_container.info("Agent is researching... this takes 30-60 seconds.")

        with st.spinner("Agent working..."):
            log_lines = []

            start = time.time()
            result = run_research_agent(query, gemini_key, tavily_key)
            elapsed = round(time.time() - start, 1)

            # Update activity log
            for line in result["search_log"]:
                log_lines.append(line)

            log_container.markdown("\n\n".join(log_lines))
            st.caption(f"Completed in {elapsed}s · {result['iterations']} iterations")

        # Render report
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
            