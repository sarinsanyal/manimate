import subprocess
import glob
from graph.state import GraphState


def render_scene(scene_name: str, code: str, index: int) -> tuple[bool, str]:
    filename = f"scene_{index}.py"
    with open(filename, "w") as f:
        f.write(code)

    result = subprocess.run(
        ["manim", "-ql", filename, scene_name],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        return False, result.stderr

    matches = glob.glob(f"media/videos/scene_{index}/*/{scene_name}.mp4")
    if matches:
        return True, matches[0]
    return False, "Render reported success but output file not found."


def render_sandbox_node(state: GraphState) -> GraphState:
    rendered_clips = []
    failed_scenes = []

    for i, scene in enumerate(state["scenes"]):
        success, result = render_scene(scene["scene_name"], scene["code"], i)
        if success:
            rendered_clips.append(result)
            print(f"  ✓ Rendered {scene['scene_name']}")
        else:
            print(f"  ✗ Failed {scene['scene_name']}: {result[:200]}")
            failed_scenes.append({**scene, "error": result, "index": i})

    return {**state, "rendered_clips": rendered_clips, "failed_scenes": failed_scenes}