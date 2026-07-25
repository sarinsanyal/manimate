from langgraph.graph import StateGraph, END
from graph.state import GraphState
from graph.solve_problem import solve_node

graph = StateGraph(GraphState)
graph.add_node("solve", solve_node)
graph.set_entry_point("solve")
graph.add_edge("solve", END)

app = graph.compile()