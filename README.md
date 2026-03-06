# SearchLoop — Autonomous Research Agent

An LLM-powered agentic pipeline that self-directs multi-step web research using tool-calling loops to produce structured reports, without human intervention at each step.

## Demo
[View Live Demo](https://searchloop.streamlit.app/)
> **Query:** "What are the latest advances in vision transformers for medical imaging?"

The agent autonomously breaks this into sub-questions, searches the web iteratively, evaluates whether it has sufficient coverage, and synthesizes a structured report.

---

## Architecture

```
User Query
    │
    ▼
┌─────────────────────────────────────┐
│           Gemini (LLM)              │
│                                     │
│  1. Decompose query into            │
│     sub-questions                   │
│                                     │
│  2. Decide: search_web OR           │
│     finalize_report                 │
└──────────┬──────────────────────────┘
           │ tool_call: search_web
           ▼
┌─────────────────────────────────────┐
│         Tavily Search API           │
│  Returns top-5 web results          │
└──────────┬──────────────────────────┘
           │ tool_result
           ▼
┌─────────────────────────────────────┐
│           Gemini (LLM)              │
│                                     │
│  Evaluate: "Do I have enough        │
│  information?"                      │
│                                     │
│  NO  ──► loop back, refine query    │
│  YES ──► call finalize_report       │
└──────────┬──────────────────────────┘
           │ tool_call: finalize_report
           ▼
┌─────────────────────────────────────┐
│        Structured Report            │
│  • Title & Summary                  │
│  • Sections with content            │
│  • Key Findings                     │
│  • Sources                          │
└─────────────────────────────────────┘
```

**What makes it agentic:** The LLM autonomously decides *what* to search, *when* it has enough information, and *when* to stop — the loop runs without human input at each step. This is Gemini's native tool-calling used as an agent planning mechanism.

---

## Stack

- **[Gemini API](https://aistudio.google.com)** — LLM backbone, tool-calling for agent loop
- **[Tavily](https://tavily.com)** — real-time web search API
- **[Streamlit](https://streamlit.io)** — UI

---

## Setup

### 1. Clone the repo
```bash
git clone https://github.com/Srijani-Das07/SearchLoop
cd SearchLoop
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set API keys

Either export them:
```bash
export GEMINI_API_KEY=your_key_here
export TAVILY_API_KEY=your_key_here
```

Or enter them directly in the sidebar when the app runs.

### 4. Run
```bash
streamlit run app.py
```

---

## How to use

1. Enter your API keys in the sidebar
2. Type a research query
3. Click **Research**
4. Watch the agent work in real-time (left panel)
5. Read the structured report (right panel)

---

## Example queries

- "What are the latest advances in vision transformers for medical imaging?"
- "How does retrieval-augmented generation improve LLM accuracy?"
- "What is the current state of quantum computing hardware?"
- "Compare transformer vs Mamba architectures for sequence modeling"

---

## Project Structure

```
SearchLoop/
├── app.py              # Streamlit UI
├── src/
│   └── agent.py        # Core agent loop (tool-calling + LLM)
├── requirements.txt
└── README.md
```
