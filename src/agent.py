import google.generativeai as genai
from tavily import TavilyClient

def run_research_agent(query: str, gemini_api_key: str, tavily_api_key: str) -> dict:
    genai.configure(api_key=gemini_api_key)
    tavily = TavilyClient(api_key=tavily_api_key)

    search_log = []
    sources = []

    def search_web(search_query: str) -> str:
        search_log.append(f"🔍 Searching: {search_query}")
        try:
            results = tavily.search(query=search_query, max_results=5)
            formatted = []
            for r in results.get("results", []):
                sources.append(r["url"])
                formatted.append(f"Title: {r['title']}\nURL: {r['url']}\nContent: {r['content']}\n")
            return "\n---\n".join(formatted)
        except Exception as e:
            error_msg = str(e)
            search_log.append(f"⚠️ Search failed: {error_msg[:80]}")
            return f"Search failed: {error_msg}"

    tools = [
        {
            "function_declarations": [
                {
                    "name": "search_web",
                    "description": "Search the web for information on a specific query. Call this multiple times with different queries to gather comprehensive information.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "The specific search query"
                            }
                        },
                        "required": ["query"]
                    }
                },
                {
                    "name": "finalize_report",
                    "description": "Call this ONLY when you have gathered enough information from multiple searches to write a complete report. Search at least 3-4 times before calling this.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "title": {
                                "type": "string",
                                "description": "Title of the research report"
                            },
                            "summary": {
                                "type": "string",
                                "description": "Executive summary in 2-3 sentences"
                            },
                            "sections": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "heading": {"type": "string"},
                                        "content": {"type": "string"}
                                    }
                                },
                                "description": "Main sections of the report, each with a heading and detailed content"
                            },
                            "key_findings": {
                                "type": "array",
                                "items": {"type": "string"},
                                "description": "3-5 key findings as concise bullet points"
                            }
                        },
                        "required": ["title", "summary", "sections", "key_findings"]
                    }
                }
            ]
        }
    ]

    system_prompt = """You are an autonomous research agent. Your job is to thoroughly research a topic by:
1. Breaking the query into specific sub-questions
2. Searching for each sub-question using search_web
3. Evaluating if you have enough information — if not, search again with refined queries
4. Only calling finalize_report when you have comprehensive coverage from multiple searches

Be rigorous. Always search at least 3-4 times before finalizing."""

    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",
        tools=tools,
        system_instruction=system_prompt
    )

    chat = model.start_chat()
    final_report = None
    iterations = 0
    max_iterations = 10

    response = chat.send_message(f"Research this topic thoroughly: {query}")

    while iterations < max_iterations:
        iterations += 1
        tool_results = []
        should_finalize = False

        has_tool_call = False
        for part in response.parts:
            if hasattr(part, "function_call") and part.function_call.name:
                has_tool_call = True
                fn = part.function_call
                args = dict(fn.args)

                if fn.name == "search_web":
                    result = search_web(args["query"])
                    tool_results.append({
                        "function_response": {
                            "name": "search_web",
                            "response": {"result": result}
                        }
                    })

                elif fn.name == "finalize_report":
                    search_log.append("✅ Report finalized")
                    final_report = {
                        "title": args.get("title", "Research Report"),
                        "summary": args.get("summary", ""),
                        "sections": args.get("sections", []),
                        "key_findings": args.get("key_findings", []),
                        "sources": list(set(sources))
                    }
                    tool_results.append({
                        "function_response": {
                            "name": "finalize_report",
                            "response": {"result": "Report successfully generated."}
                        }
                    })
                    should_finalize = True

        if not has_tool_call:
            response = chat.send_message("Please continue researching using the search_web tool, then finalize with finalize_report.")
            continue

        if tool_results:
            response = chat.send_message(tool_results)

        if should_finalize:
            break

    return {
        "report": final_report,
        "search_log": search_log,
        "iterations": iterations
    }