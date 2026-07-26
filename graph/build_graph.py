from langgraph.graph import StateGraph, END
from graph.state import GraphState
from graph.explain_topic import explain_topic_node
from graph.verify_steps import verify_steps_node
from graph.generate_code import generate_code_node
from graph.render import render_sandbox_node
from graph.retry_code import retry_failed_scenes_node

graph = StateGraph(GraphState)

graph.add_node("explain", explain_topic_node)
graph.add_node("verify", verify_steps_node)
graph.add_node("generate_code", generate_code_node)
graph.add_node("render", render_sandbox_node)
graph.add_node("retry_code", retry_failed_scenes_node)

graph.set_entry_point("explain")
graph.add_edge("explain", "verify")
graph.add_edge("verify", "generate_code")
graph.add_edge("generate_code", "render")


def should_retry(state):
    if not state.get("failed_scenes"):
        return "done"
    if state.get("retry_count", 0) >= 3:
        return "give_up"
    return "retry"


graph.add_conditional_edges("render", should_retry, {
    "retry": "retry_code",
    "done": END,
    "give_up": END,
})
graph.add_edge("retry_code", "render")

app = graph.compile()