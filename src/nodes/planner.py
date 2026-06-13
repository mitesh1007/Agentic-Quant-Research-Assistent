from groq import Groq
from dotenv import load_dotenv
from src.state import AgentState
import os

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def planner_node(state: AgentState) -> AgentState:
    question = state["research_question"]

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a quantitative research planner. Create a concise 4-step research plan tailored to the specific research question."
            },
            {
                "role": "user",
                "content": f"""Create a 4-step research plan to answer: '{question}'

Available tools:
- fetch_data(ticker, period): fetches OHLCV summary. Use correct ticker for the question.
  Tickers: "^NSEI" for Nifty 50, "^BSESN" for Sensex, "AAPL" for Apple, "^GSPC" for S&P 500
- compute_stats(ticker, period, hypothesis): hypothesis must be exactly "momentum", "mean_reversion", or "normality"
- search_arxiv(query): finds research papers
- run_code(code): runs Python. Always download data inside code using yfinance. Never read files.

IMPORTANT:
- Tailor each step specifically to the research question
- Step 2 must use compute_stats with the hypothesis that best matches the question:
  - normality questions → hypothesis="normality"
  - mean reversion questions → hypothesis="mean_reversion"
  - momentum questions → hypothesis="momentum"
- Step 4 must use run_code to implement a Python analysis directly testing the research question

Output exactly 4 steps, one sentence each."""
            }
        ],
        temperature=0.1,
        max_tokens=400
    )

    plan = response.choices[0].message.content.strip()
    print(f"\nPLAN:\n{plan}\n")

    return {
        "plan": plan,
        "messages": [],
        "tool_results": [],
        "iteration_count": 0,
        "report": "",
        "research_question": question
    }