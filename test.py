from src.nodes.planner import planner_node
from src.nodes.groq_node import groq_node

state = {
    "research_question": "Does momentum effect exist in Nifty 50?",
    "plan": "",
    "messages": [],
    "tool_results": [],
    "report": "",
    "iteration_count": 0
}

state = planner_node(state)
state = groq_node(state)