from graph.llm_config import get_coder_llm, get_reasoning_llm
from graph.state import GraphState
from graph.extract import extract_code
from graph.diagram_builder import build_diagram_scene, ICON_ALLOWLIST
import textwrap
import json
import re

CODER_MODEL = "qwen2.5-coder:3b"


def wrap_text(text: str, width: int = 40) -> str:
    """Pre-wrap text into multiple lines so Manim's Text() renders it with \\n line breaks."""
    wrapped = textwrap.fill(text.strip(), width=width)
    return wrapped.replace("\n", "\\n")


COMMON_RULES = """
It must contain:
- The import line: from manim import *
- A class named {scene_name} that inherits from Scene
- A construct(self) method with the animation logic

The narration and display text given to you below are ALREADY wrapped with line breaks (\\n) so they fit on screen. Use them exactly as given — do not join lines back together, do not add your own line breaks, do not scale text width.

Layout rule — title and body must never overlap:
- title = Text(narration, font_size=28), positioned with title.to_edge(UP, buff=0.5)
- body (if present) must be positioned relative to the title using body.next_to(title, DOWN, buff=0.8) — never use body.move_to(ORIGIN) if a title is also present, since that can overlap.

You may ONLY use these methods/functions inside construct() — do not invent any others:
- Text(...), MathTex(...)
- Positioning (call directly on the object, NOT inside self.play()): .to_edge(UP), .to_edge(DOWN), .move_to(...), .next_to(other, direction, buff=...), .shift(...)
- Animations (only these go inside self.play()): Write(x), FadeIn(x), FadeOut(x), TransformMatchingTex(a, b), Indicate(x, color=YELLOW), Create(x)
- self.wait(seconds)
- Rectangle(...), Circle(...), Line(...), Arrow(...), VGroup(...)

Never invent animation names. self.play() may ONLY contain the animation functions listed above — nothing else.

Return ONLY the complete Python file, wrapped in a single ```python code fence. Do not add any explanation before or after the code fence.
"""


def build_prompt_equation(step, scene_name):
    narration = wrap_text(step['narration'], width=40)
    return f"""Write a complete Manim Community Edition Python file.
{COMMON_RULES.format(scene_name=scene_name)}
Goal: teach this step of a concept, showing a piece of math notation.
Narration (already wrapped, use as-is): "{narration}"
Notation to display: "{step.get('display') or ''}"

Requirements for construct():
- title = Text("{narration}", font_size=28), positioned title.to_edge(UP, buff=0.5), animated with self.play(Write(title))
- eq = MathTex(the notation), positioned eq.next_to(title, DOWN, buff=0.8)
- self.play(Write(eq))
- self.wait(2)
"""


def build_prompt_highlight_text(step, scene_name):
    narration = wrap_text(step['narration'], width=40)
    body_text = wrap_text(step.get('display') or '', width=30)
    return f"""Write a complete Manim Community Edition Python file.
{COMMON_RULES.format(scene_name=scene_name)}
Goal: teach this step by showing a sentence or phrase clearly on screen.
Narration (already wrapped, use as-is): "{narration}"
Text to display (already wrapped, use as-is): "{body_text}"

Requirements for construct():
- title = Text("{narration}", font_size=26), title.to_edge(UP, buff=0.5), self.play(Write(title))
- body = Text("{body_text}", font_size=32), body.next_to(title, DOWN, buff=0.8)
- self.play(Write(body))
- self.wait(2)
"""


def build_prompt_generic(step, scene_name):
    narration = wrap_text(step['narration'], width=40)
    display_text = wrap_text(step.get('display') or '', width=30)
    return f"""Write a complete Manim Community Edition Python file.
{COMMON_RULES.format(scene_name=scene_name)}
Goal: visually teach this step of a concept to a student. Keep the animation simple and clear given the limited allowed methods.
Narration (already wrapped, use as-is): "{narration}"
Content to display, if any (already wrapped, use as-is): "{display_text}"
Suggested visual style: {step.get('visual_hint') or 'none'}

Requirements for construct():
- title = Text("{narration}", font_size=26), title.to_edge(UP, buff=0.5), animated in
- If there is content to display, show it using body.next_to(title, DOWN, buff=0.8), animated in
- Keep it to 2-4 animation calls total
- self.wait(1) between animations so it's readable
"""

PROMPT_BUILDERS = {
    "equation": build_prompt_equation,
    "highlight_text": build_prompt_highlight_text,
}

def get_diagram_stages(step) -> list[dict]:
    llm = get_reasoning_llm()
    allowlist_str = ", ".join(ICON_ALLOWLIST)
    prompt = f"""Break this narration into 2 or 3 short stages for a diagram. For each stage, pick the closest matching icon from this exact list (use the icon name exactly as written, do not invent new names): {allowlist_str}

If nothing fits well, use "circle" as a neutral fallback icon.

Narration: "{step['narration']}"

Return ONLY valid JSON, no other text: {{"stages": [{{"icon": "icon-name", "label": "1-3 word label"}}]}}"""

    response = llm.invoke(prompt)
    from graph.extract import extract_code
    cleaned = extract_code(response.content)
    cleaned = re.sub(r'\\(?!["\\/])', r'\\\\', cleaned)
    try:
        data = json.loads(cleaned)
        stages = data.get("stages", [])
        if stages:
            return stages
    except Exception:
        pass
    return [{"icon": "circle", "label": "Stage 1"}, {"icon": "circle", "label": "Stage 2"}]

def generate_code_node(state: GraphState) -> GraphState:
    llm = get_coder_llm()
    all_scenes = []

    for i, step in enumerate(state["steps"]):
        scene_name = f"Step{i+1}Scene"

        if step.get("visual_hint") == "diagram":
            stages = get_diagram_stages(step)
            code = build_diagram_scene(scene_name, wrap_text(step['narration'], width=40), stages)
        else:
            builder = PROMPT_BUILDERS.get(step.get("visual_hint"), build_prompt_generic)
            prompt = builder(step, scene_name)
            response = llm.invoke(prompt)
            code = extract_code(response.content)

        all_scenes.append({"scene_name": scene_name, "code": code})

    return {**state, "scenes": all_scenes}