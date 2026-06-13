from groq import Groq
from dotenv import load_dotenv
from src.state import AgentState
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """You are a quantitative research assistant. Analyze financial markets one step at a time.

Available tools:
1. fetch_data(ticker, period) — ticker: "^NSEI" for Nifty 50, "^BSESN" for Sensex, "AAPL" for Apple, "^GSPC" for S&P 500. period: "1y","2y","5y","10y"
2. compute_stats(ticker, period, hypothesis) — hypothesis MUST be exactly one of: "momentum", "mean_reversion", "normality"
3. search_arxiv(query) — short query string
4. run_code(code) — Python string. Rules for code:
   - ALWAYS download data inside code using yfinance
   - NEVER read from files
   - ALWAYS use dropna() after pct_change()
   - ALWAYS use data[('Close', 'TICKER')] to access close prices
   - ALWAYS print numerical results
   - ALWAYS save a matplotlib chart using plt.show() at the end
   - Use numpy, pandas, scipy, matplotlib only

STRICT RULES:
- Call ONLY ONE tool per response.
- Never repeat a tool you already called.
- After 4 tool calls you MUST call finish.
- Never hallucinate results. Only use numbers from actual tool outputs.

Response format — ONLY valid JSON, nothing else:
{
    "tool": "tool_name",
    "args": {"arg1": "value1"}
}

To finish:
{
    "tool": "finish",
    "args": {"summary": "findings with real numbers from tool results"}
}"""


def groq_node(state: AgentState) -> AgentState:
    iteration = state.get("iteration_count", 0)

    if iteration >= 8:
        return {
            "messages": state.get("messages", []),
            "tool_results": state.get("tool_results", []),
            "iteration_count": iteration,
            "report": "Max iterations reached.",
            "research_question": state["research_question"],
            "plan": state.get("plan", "")
        }

    messages = state.get("messages", [])

    if iteration == 0:
        messages = [{
            "role": "user",
            "content": f"""Research Question: {state['research_question']}

Plan:
{state.get('plan', '')}

You have exactly 4 tool calls then call finish.
Start with fetch_data. Choose the right ticker based on the research question.
On your 4th tool call, use run_code to write Python code that directly tests the research question with real data and saves a matplotlib chart."""
        }]

    trimmed = messages[-6:] if len(messages) > 6 else messages

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[{"role": "system", "content": SYSTEM_PROMPT}] + trimmed,
        temperature=0.1,
        max_tokens=1500
    )

    reply = response.choices[0].message.content.strip()

    if "```json" in reply:
        reply = reply.split("```json")[1].split("```")[0].strip()
    elif "```" in reply:
        reply = reply.split("```")[1].split("```")[0].strip()

    print(f"\nAGENT [{iteration+1}]:\n{reply}\n")

    new_messages = messages + [{"role": "assistant", "content": reply}]

    return {
        "messages": new_messages,
        "tool_results": state.get("tool_results", []),
        "iteration_count": iteration + 1,
        "report": state.get("report", ""),
        "research_question": state["research_question"],
        "plan": state.get("plan", "")
    }