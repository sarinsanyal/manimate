from langchain_ollama import ChatOllama
from graph.state import GraphState
from graph.extract import extract_code


def retry_failed_scenes_node(state: GraphState) -> GraphState:
    llm = ChatOllama(model="qwen2.5-coder:3b", temperature=0)
    fixed_scenes = list(state["scenes"])  # copy

    for failed in state["failed_scenes"]:
        prompt = f"""This Manim code failed to run with this error:

{failed['error'][-800:]}

Here is the code that failed:
```python
{failed['code']}
```

Fix the code so it runs without error. Keep the same class name and overall goal. Return ONLY the corrected complete Python file, wrapped in a single ```python code fence."""

        response = llm.invoke(prompt)
        new_code = extract_code(response.content)
        fixed_scenes[failed["index"]] = {"scene_name": failed["scene_name"], "code": new_code}

    retry_count = state.get("retry_count", 0) + 1
    return {**state, "scenes": fixed_scenes, "retry_count": retry_count}