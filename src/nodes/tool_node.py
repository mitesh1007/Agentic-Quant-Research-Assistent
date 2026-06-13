import json
from src.state import AgentState
from src.tools.fetch_data import fetch_data
from src.tools.run_code import run_code
from src.tools.search_arxiv import search_arxiv
from src.tools.compute_stats import compute_stats


def tool_node(state: AgentState) -> AgentState:
    messages = state.get("messages", [])
    tool_results = state.get("tool_results", [])

    if not messages:
        return state

    last_message = messages[-1]["content"]

    try:
        cleaned = last_message.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0].strip()

        tool_call = json.loads(cleaned)
        tool_name = tool_call.get("tool")
        args = tool_call.get("args", {})

        print(f"\n TOOL CALL: {tool_name}")

        if tool_name == "fetch_data":
            result = fetch_data(
                ticker=args.get("ticker", "^NSEI"),
                period=args.get("period", "1y")
            )

        elif tool_name == "run_code":
            result = run_code(code=args.get("code", ""))

        elif tool_name == "search_arxiv":
            result = search_arxiv(
                query=args.get("query", ""),
                max_results=args.get("max_results", 3)
            )

        elif tool_name == "compute_stats":
            result = compute_stats(
                ticker=args.get("ticker", "^NSEI"),
                period=args.get("period", "1y"),
                hypothesis=args.get("hypothesis", "momentum")
            )

        elif tool_name == "finish":
            summary = args.get("summary", "")
            print(f"\n AGENT FINISHED:\n{summary}")
            return {
                "messages": messages,
                "tool_results": tool_results + [summary],
                "iteration_count": state.get("iteration_count", 0),
                "report": summary,
                "research_question": state["research_question"],
                "plan": state.get("plan", "")
            }

        else:
            result = f"Unknown tool: {tool_name}"

        print(f" RESULT PREVIEW: {str(result)[:200]}...\n")

        new_messages = messages + [{
            "role": "user",
            "content": f"Tool '{tool_name}' result:\n{result}\n\nContinue the research. What is your next step?"
        }]

        return {
            "messages": new_messages,
            "tool_results": tool_results + [result],
            "iteration_count": state.get("iteration_count", 0),
            "report": state.get("report", ""),
            "research_question": state["research_question"],
            "plan": state.get("plan", "")
        }

    except json.JSONDecodeError:
        print(f" Could not parse JSON, treating as finish.")
        return {
            "messages": messages,
            "tool_results": tool_results,
            "iteration_count": state.get("iteration_count", 0),
            "report": last_message,
            "research_question": state["research_question"],
            "plan": state.get("plan", "")
        }