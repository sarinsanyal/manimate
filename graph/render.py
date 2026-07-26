import subprocess
import glob
import os
import re
from graph.state import GraphState

SANDBOX_DIR = "render_sandbox"


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "_", text.strip().lower())
    return slug.strip("_")[:40]


def render_scene(scene_name: str, code: str, index: int, topic_slug: str) -> tuple[bool, str]:
    os.makedirs(SANDBOX_DIR, exist_ok=True)

    unique_id = f"{topic_slug}_{index}"
    filename = os.path.join(SANDBOX_DIR, f"scene_{unique_id}.py")
    with open(filename, "w") as f:
        f.write(code)

    result = subprocess.run(
        ["manim", "-ql", filename, scene_name, "--media_dir", os.path.join(SANDBOX_DIR, "media")],
        capture_output=True, text=True
    )

    if result.returncode != 0:
        log_path = os.path.join(SANDBOX_DIR, f"error_{unique_id}_{scene_name}.log")
        with open(log_path, "w", encoding="utf-8") as f:
            f.write("STDOUT:\n")
            f.write(result.stdout)
            f.write("\n\nSTDERR:\n")
            f.write(result.stderr)
        return False, result.stderr

    matches = glob.glob(f"{SANDBOX_DIR}/media/videos/scene_{unique_id}/*/{scene_name}.mp4")
    if matches:
        return True, matches[0]
    return False, "Render reported success but output file not found."


def render_sandbox_node(state: GraphState) -> GraphState:
    rendered_clips = []
    failed_scenes = []
    topic_slug = _slugify(state.get("topic", "topic"))

    for i, scene in enumerate(state["scenes"]):
        success, result = render_scene(scene["scene_name"], scene["code"], i, topic_slug)
        if success:
            rendered_clips.append(result)
            print(f"  ✓ Rendered {scene['scene_name']}")
        else:
            print(f"  ✗ Failed {scene['scene_name']}: {result[:200]}")
            print(f"     Full log: {SANDBOX_DIR}/error_{topic_slug}_{i}_{scene['scene_name']}.log")
            failed_scenes.append({**scene, "error": result, "index": i})

    return {**state, "rendered_clips": rendered_clips, "failed_scenes": failed_scenes}