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

Read the document text below and identify up to {MAX_TOPICS} distinct topics covered in it. For each topic, give a short title AND a 2-4 sentence excerpt copied or closely paraphrased from the document that captures what THIS specific topic actually covers. The excerpt exists so a separate teacher can explain the correct concept later without seeing the whole document — be specific enough to disambiguate the topic (e.g. if the title could be misread as an unrelated meaning of the same words, the excerpt should make the actual subject unambiguous).

If the document covers fewer than {MAX_TOPICS} topics, return only that many. Do not invent topics that are not actually in the text.

Return ONLY valid JSON in this exact format, no other text, no markdown fences:
{{"topics": [{{"title": "short topic title", "excerpt": "2-4 sentences of relevant source content"}}]}}

Example:
{{"topics": [{{"title": "Subtracting integers", "excerpt": "When subtracting a negative number, we add its absolute value instead. For example, 5 - (-3) becomes 5 + 3 = 8."}}]}}

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

    print(f"  Segmented into {len(topics)} topic(s): {[t['title'] for t in topics]}")

    return {**state, "topics": topics}