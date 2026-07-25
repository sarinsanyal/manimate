from langgraph.graph import StateGraph, END
from graph.state import GraphState
from graph.solve_problem import solve_node
from graph.verify_steps import verify_steps_node

graph = StateGraph(GraphState)
graph.add_node("solve", solve_node)
graph.add_node("verify", verify_steps_node)

graph.set_entry_point("solve")
graph.add_edge("solve", "verify")
graph.add_edge("verify", END)

app = graph.compile()