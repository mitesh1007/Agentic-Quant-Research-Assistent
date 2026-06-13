from typing import TypedDict, Annotated
import operator

class AgentState(TypedDict):
    research_question: str
    plan: str
    messages: Annotated[list, operator.add]
    tool_results: Annotated[list, operator.add]
    report: str
    iteration_count: int