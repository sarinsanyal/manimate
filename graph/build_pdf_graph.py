from langgraph.graph import StateGraph, END
from graph.state import GraphState
from graph.extract_pdf import extract_pdf_node
from graph.segment_topics import segment_topics_node

pdf_graph = StateGraph(GraphState)

pdf_graph.add_node("extract_pdf", extract_pdf_node)
pdf_graph.add_node("segment_topics", segment_topics_node)

pdf_graph.set_entry_point("extract_pdf")
pdf_graph.add_edge("extract_pdf", "segment_topics")
pdf_graph.add_edge("segment_topics", END)

pdf_app = pdf_graph.compile()