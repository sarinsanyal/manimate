from langchain_ollama import ChatOllama
import json
import re
from graph.state import GraphState


def solve_node(state: GraphState) -> GraphState:
    llm = ChatOllama(model="qwen2.5:1.5b", temperature=0)

    prompt = f"""Solve this problem step by step. Every from_expr and to_expr MUST be a complete equation showing both sides (never drop the "= ..." part). Return ONLY valid JSON, no other text, no markdown fences, in this exact format:

{{"steps": [{{"narration": "explanation of this step", "from_expr": "current equation", "to_expr": "equation after this step"}}]}}

Example for "Solve for x: 2x + 4 = 10":
{{"steps": [
  {{"narration": "Subtract 4 from both sides", "from_expr": "2x + 4 = 10", "to_expr": "2x = 6"}},
  {{"narration": "Divide both sides by 2", "from_expr": "2x = 6", "to_expr": "x = 3"}}
]}}

Problem: {state['problem']}"""

    response = llm.invoke(prompt)
    raw = response.content

    cleaned = re.sub(r"^```json\s*|\s*```$", "", raw.strip())
    match = re.search(r"\{.*\}", cleaned, re.DOTALL)
    if match:
        cleaned = match.group(0)

    cleaned = re.sub(r'\\(?!["\\/bfnrtu])', r'\\\\', cleaned)

    data = json.loads(cleaned)
    
    return {"problem": state["problem"], "steps": data["steps"], "raw_output": raw}