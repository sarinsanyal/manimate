from langchain_ollama import ChatOllama
import json
import re
from graph.state import GraphState
from graph.extract import extract_code


def explain_topic_node(state: GraphState) -> GraphState:
    llm = ChatOllama(model="qwen2.5:1.5b", temperature=0)

    prompt = f"""You are a teacher explaining a topic to a student seeing it for the first time. The topic could be from any subject — math, science, history, literature, grammar, civics, anything.

Break the explanation into small teaching steps, each building on the last. For each step, decide what kind of visual would help a student understand it — pick the visual_hint that best fits, or "none" if plain narration is enough.

Do not use LaTeX syntax like \( \) inside narration text — keep narration in plain English, only use the display field for notation.

Available visual_hint values: equation, graph, number_line, shape, timeline, diagram, map, comparison, highlight_text, tree, none

Return ONLY valid JSON, no other text, no markdown fences, in this exact format:
{{"steps": [
  {{"narration": "plain-English explanation of this piece", "display": "text/notation to show on screen, or null", "visual_hint": "one of the values above"}}
]}}

Example for "The Water Cycle":
{{"steps": [
  {{"narration": "Water is always moving between the ocean, sky, and land in a repeating cycle.", "display": null, "visual_hint": "diagram"}},
  {{"narration": "The sun heats water in oceans and lakes, causing it to evaporate into vapor.", "display": "Evaporation", "visual_hint": "diagram"}},
  {{"narration": "As vapor rises and cools, it condenses into clouds.", "display": "Condensation", "visual_hint": "diagram"}}
]}}

Example for "Subject and predicate":
{{"steps": [
  {{"narration": "Every complete sentence has two parts: a subject, who or what the sentence is about, and a predicate, what the subject does.", "display": null, "visual_hint": "none"}},
  {{"narration": "In 'The dog runs fast', 'The dog' is the subject and 'runs fast' is the predicate.", "display": "The dog runs fast", "visual_hint": "highlight_text"}}
]}}

Topic to teach: {state['topic']}"""

    response = llm.invoke(prompt)
    raw = response.content
    cleaned = extract_code(raw)
    cleaned = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', cleaned)
    data = json.loads(cleaned)

    return {"topic": state["topic"], "steps": data["steps"], "raw_output": raw}