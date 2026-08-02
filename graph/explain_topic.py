from graph.llm_config import get_reasoning_llm
import json
import re
from graph.state import GraphState
from graph.extract import extract_code


def explain_topic_node(state: GraphState) -> GraphState:
    llm = get_reasoning_llm()

    excerpt = state.get("topic_excerpt")
    context_block = f'\nSource material for this exact topic (use this to ground your explanation — do not explain a different or more general meaning of these words):\n"""{excerpt}"""\n' if excerpt else ""

    prompt = f"""You are a teacher explaining a topic to a student for the first time. The topic can be from any subject: math, science, history, literature, grammar, or anything else.
{context_block}
Break your explanation into small steps, each building on the last. For each step, pick a visual_hint that fits: equation, graph, number_line, shape, timeline, diagram, map, comparison, highlight_text, tree, or none.

Narration must be plain spoken English — no LaTeX, no math symbols, no backslashes. Put any notation in the display field instead.

Return ONLY valid JSON in this exact format, no other text, no markdown fences:
{{"steps": [
  {{"narration": "plain English explanation", "display": "notation to show, or null", "visual_hint": "one of the values above"}}
]}}

Example for "The Water Cycle":
{{"steps": [
  {{"narration": "Water is always moving between the ocean, sky, and land in a repeating cycle.", "display": null, "visual_hint": "none"}}
]}}

Topic to teach: {state['topic']}"""

    response = llm.invoke(prompt)
    raw = response.content
    cleaned = extract_code(raw)
    cleaned = re.sub(r'\\(?!["\\/])', r'\\\\', cleaned)
    data = json.loads(cleaned)

    for step in data["steps"]:
      text = step["narration"]
      text = re.sub(r'\\[a-zA-Z]+\{[^}]*\}(\{[^}]*\})?', '', text)  # \frac{a}{b}, \sqrt{a}, etc.
      text = re.sub(r'\\[()[\]]', '', text)                          # \( \) \[ \]
      text = re.sub(r'\s{2,}', ' ', text)                             # collapse leftover double spaces
      step["narration"] = text.strip()
      
    return {"topic": state["topic"], "steps": data["steps"], "raw_output": raw}