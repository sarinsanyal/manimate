from langchain_ollama import ChatOllama
import json
import re
from graph.state import GraphState
from graph.extract import extract_code


def explain_topic_node(state: GraphState) -> GraphState:
    llm = ChatOllama(model="qwen2.5:1.5b", temperature=0, num_predict=800)

    prompt = f"""You are a teacher explaining a topic to a student for the first time. The topic can be from any subject: math, science, history, literature, grammar, or anything else.

Break your explanation into small steps, each building on the last. For each step, pick a visual_hint that fits: equation, graph, number_line, shape, timeline, diagram, map, comparison, highlight_text, tree, or none.

Narration must be plain spoken English — no LaTeX, no math symbols, no backslashes. Put any notation in the display field instead.

Return ONLY valid JSON in this exact format, no other text, no markdown fences:
{{"steps": [
  {{"narration": "plain English explanation", "display": "notation to show, or null", "visual_hint": "one of the values above"}}
]}}

Example for "The Water Cycle":
{{"steps": [
  {{"narration": "Water is always moving between the ocean, sky, and land in a repeating cycle.", "display": null, "visual_hint": "none"}},
  {{"narration": "The sun heats water in oceans and lakes, causing it to evaporate into vapor.", "display": "Evaporation", "visual_hint": "diagram"}},
  {{"narration": "As vapor rises and cools, it condenses into clouds.", "display": "Condensation", "visual_hint": "diagram"}},
  {{"narration": "The clouds release the water as rain or snow, which flows back into rivers and oceans.", "display": "Precipitation", "visual_hint": "diagram"}}
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