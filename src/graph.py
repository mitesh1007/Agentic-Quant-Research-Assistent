from langgraph.graph import StateGraph, END
from src.state import AgentState
from src.nodes.planner import planner_node
from src.nodes.groq_node import groq_node
from src.nodes.tool_node import tool_node
from src.nodes.report_node import report_node
import json

def should_continue(state: AgentState) -> str:
    """
    Router — decides whether to call a tool, finish, or hit the limit.
    """
    messages = state.get("messages", [])
    iteration = state.get("iteration_count", 0)
    
    if iteration >= 10:
        return "report"
    
    if not messages:
        return "report"
    
    last_message = messages[-1]["content"]
    
    try:
        cleaned = last_message.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        elif "```" in cleaned:
            cleaned = cleaned.split("```")[1].split("```")[0].strip()
        
        tool_call = json.loads(cleaned)
        
        if tool_call.get("tool") == "finish":
            return "report"
        else:
            return "tool"
    except:
        return "report"

def build_graph():
    graph = StateGraph(AgentState)
    
    # add nodes
    graph.add_node("planner", planner_node)
    graph.add_node("agent", groq_node)
    graph.add_node("tool", tool_node)
    graph.add_node("report", report_node)
    
    # entry point
    graph.set_entry_point("planner")
    
    # edges
    graph.add_edge("planner", "agent")
    
    # conditional edge — agent decides tool or finish
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "tool": "tool",
            "report": "report"
        }
    )
    
    # after tool runs, go back to agent
    graph.add_edge("tool", "agent")
    
    # report is the end
    graph.add_edge("report", END)
    
    return graph.compile()