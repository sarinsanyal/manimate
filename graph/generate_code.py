from langchain_ollama import ChatOllama
from graph.state import GraphState
from graph.extract import extract_code
import textwrap

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

def build_prompt_diagram(step, scene_name):
    narration = wrap_text(step['narration'], width=40)
    display_hint = step.get('display') or ''
    return f"""Write a complete Manim Community Edition Python file.
{COMMON_RULES.format(scene_name=scene_name)}
Goal: visually teach this step using a simple flow diagram — shapes connected by arrows, not just text.
Narration (already wrapped, use as-is): "{narration}"
Key term for this step, if any: "{display_hint}"

Identify 2 or 3 short stages/parts implied by the narration (each label must be 1-3 words, e.g. "Sun heats water", "Evaporation", "Water vapor rises"). Pick labels that make sense for THIS narration specifically.

Requirements for construct():
- title = Text("{narration}", font_size=26), title.to_edge(UP, buff=0.5), self.play(Write(title))
- Create 2 or 3 Circle(radius=1.1, stroke_width=6) shapes, positioned left to right below the title using .move_to and .shift(RIGHT * n) or .next_to(previous_shape, RIGHT, buff=2.0)
- Alternate circle colors in this order: BLUE, ORANGE, GREEN (first circle BLUE, second ORANGE, third GREEN if present) — set via Circle(radius=1.1, stroke_width=6, color=BLUE) etc.
- Fill each circle with a light version of its own color at low opacity: add fill_color=BLUE, fill_opacity=0.15 (matching each circle's stroke color) so it reads as a soft glowing shape, not just an outline
- Put a short Text label (font_size=22) below each circle using .next_to(circle, DOWN, buff=0.3)
- Connect each circle to the next with Arrow(start_circle.get_right(), end_circle.get_left(), color=WHITE, stroke_width=5, buff=0.1)
- Animate in order: self.play(Create(circle1)), self.play(Write(label1)), self.wait(0.3), self.play(Create(arrow1)), self.play(Create(circle2)), self.play(Write(label2)), and so on for any remaining shapes
- self.wait(2) at the end

Example structure for 2 stages:
    circle1 = Circle(radius=1.1, stroke_width=6, color=BLUE, fill_color=BLUE, fill_opacity=0.15).move_to(LEFT * 3)
    label1 = Text("Sun heats water", font_size=22).next_to(circle1, DOWN, buff=0.3)
    circle2 = Circle(radius=1.1, stroke_width=6, color=ORANGE, fill_color=ORANGE, fill_opacity=0.15).move_to(RIGHT * 3)
    label2 = Text("Evaporation", font_size=22).next_to(circle2, DOWN, buff=0.3)
    arrow1 = Arrow(circle1.get_right(), circle2.get_left(), color=WHITE, stroke_width=5, buff=0.1)
"""

PROMPT_BUILDERS = {
    "equation": build_prompt_equation,
    "highlight_text": build_prompt_highlight_text,
    "diagram": build_prompt_diagram,
}


def generate_code_node(state: GraphState) -> GraphState:
    llm = ChatOllama(model=CODER_MODEL, temperature=0)
    all_scenes = []

    for i, step in enumerate(state["steps"]):
        scene_name = f"Step{i+1}Scene"
        builder = PROMPT_BUILDERS.get(step.get("visual_hint"), build_prompt_generic)
        prompt = builder(step, scene_name)

        response = llm.invoke(prompt)
        code = extract_code(response.content)

        all_scenes.append({"scene_name": scene_name, "code": code})

    return {**state, "scenes": all_scenes}