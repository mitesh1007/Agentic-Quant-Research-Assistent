import sys
from src.graph import build_graph

def run_research(question: str):
    print(f"\nRESEARCH QUESTION: {question}")
    print("="*60)

    graph = build_graph()

    initial_state = {
        "research_question": question,
        "plan": "",
        "messages": [],
        "tool_results": [],
        "report": "",
        "iteration_count": 0
    }

    final_state = graph.invoke(initial_state)

    print("\n" + "="*60)
    print("RESEARCH COMPLETE")
    print("="*60)
    print(final_state["report"])

if __name__ == "__main__":
    if len(sys.argv) > 1:
        question = " ".join(sys.argv[1:])
    else:
        question = "Does momentum effect exist in Nifty 50?"
    
    run_research(question)