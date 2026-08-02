from graph.llm_config import get_coder_llm
from graph.state import GraphState
from graph.extract import extract_code
from graph.generate_code import COMMON_RULES


def retry_failed_scenes_node(state: GraphState) -> GraphState:
    llm = get_coder_llm()
    fixed_scenes = list(state["scenes"])  # copy

    for failed in state["failed_scenes"]:
        scene_name = failed["scene_name"]
        prompt = f"""This Manim code failed to run with this error:

{failed['error'][-800:]}

Here is the code that failed:
```python
{failed['code']}
```

{COMMON_RULES.format(scene_name=scene_name)}

Fix the code so it runs without error, using ONLY the allowed methods listed above. A common mistake is passing a positioning method like move_to(...) into self.play() as if it were an animation — positioning methods are called directly on the object, not wrapped in self.play(). Keep the same class name and overall goal. Return ONLY the corrected complete Python file, wrapped in a single ```python code fence."""

        response = llm.invoke(prompt)
        new_code = extract_code(response.content)
        fixed_scenes[failed["index"]] = {"scene_name": scene_name, "code": new_code}

    retry_count = state.get("retry_count", 0) + 1
    return {**state, "scenes": fixed_scenes, "retry_count": retry_count}