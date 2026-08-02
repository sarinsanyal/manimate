import json
import re
import os
from graph.llm_config import get_reasoning_llm
from graph.state import GraphState
from graph.extract import extract_code
from graph.extract_pdf import MAX_TOPICS

REASONING_MODEL = "qwen2.5:1.5b"


def segment_topics_node(state: GraphState) -> GraphState:
    llm = get_reasoning_llm()

    text = state["raw_pdf_text"]

    prompt = f"""You are splitting a document into separate topics for a student to learn one at a time.

Read the document text below and identify up to {MAX_TOPICS} distinct topics covered in it. Each topic should be a short, clear phrase describing one self-contained thing to teach — similar to a section or concept title, not a full sentence.

If the document covers fewer than {MAX_TOPICS} topics, return only that many. Do not invent topics that are not actually in the text.

Return ONLY valid JSON in this exact format, no other text, no markdown fences:
{{"topics": ["first topic", "second topic"]}}

Example:
{{"topics": ["Subtracting integers", "Solving one-step equations", "The distributive property"]}}

Document text:
{text[:20000]}"""

    response = llm.invoke(prompt)
    raw = response.content
    cleaned = extract_code(raw)
    cleaned = re.sub(r'\\(?!["\\/])', r'\\\\', cleaned)
    data = json.loads(cleaned)

    topics = data["topics"][:MAX_TOPICS]

    if not topics:
        raise ValueError("segment_topics produced no topics from the extracted PDF text.")

    print(f"  Segmented into {len(topics)} topic(s): {topics}")

    return {**state, "topics": topics}