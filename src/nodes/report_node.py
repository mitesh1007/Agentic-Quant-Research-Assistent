from groq import Groq
from dotenv import load_dotenv
from src.state import AgentState
import os
import time
from datetime import datetime

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))


def report_node(state: AgentState) -> AgentState:
    tool_results = state.get("tool_results", [])
    question = state["research_question"]
    plan = state.get("plan", "")

    valid_results = [str(r)[:800] for r in tool_results if r and str(r).strip()]

    if not valid_results:
        all_results = "No tool results were collected."
    else:
        # reverse so most recent results (backtest) appear first
        all_results = "\n\n---\n\n".join(reversed(valid_results))

    if len(all_results) > 3000:
        all_results = all_results[:3000]

    time.sleep(3)

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "You are a quantitative research analyst. Write professional reports using ONLY actual data provided. Never invent numbers. Be concise and factual."
            },
            {
                "role": "user",
                "content": f"""Write a research report using only the data below.

Research Question: {question}

Actual Tool Results:
{all_results}

Format:
# [Title]
## Executive Summary
## Research Question
## Methodology
## Results & Analysis
## Conclusion
## Limitations

Only use numbers from the tool results above. Do not invent any statistics.
Make sure to include ALL numbers from the backtest results including annualized returns and Sharpe ratios."""
            }
        ],
        temperature=0.1,
        max_tokens=1500
    )

    report = response.choices[0].message.content.strip()

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"outputs/report_{timestamp}.md"

    with open(filename, "w", encoding="utf-8") as f:
        f.write(f"**Research Question:** {question}\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(report)

    print(f"\n Report saved to {filename}")

    return {
        "report": report,
        "messages": state.get("messages", []),
        "tool_results": tool_results,
        "iteration_count": state.get("iteration_count", 0),
        "research_question": question,
        "plan": plan
    }