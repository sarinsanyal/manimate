from langchain_ollama import ChatOllama
from graph.state import GraphState
from graph.extract import extract_code

CODER_MODEL = "qwen2.5-coder:3b"

COMMON_RULES = """
It must contain:
- The import line: from manim import *
- A class named {scene_name} that inherits from Scene
- A construct(self) method with the animation logic

You may ONLY use these methods/functions inside construct() — do not invent any others:
- Text(...), MathTex(...)
- Positioning (call directly on the object, NOT inside self.play()): .to_edge(UP), .to_edge(DOWN), .move_to(...), .next_to(other, direction), .shift(...)
- Animations (only these go inside self.play()): Write(x), FadeIn(x), FadeOut(x), TransformMatchingTex(a, b), Indicate(x, color=YELLOW), Create(x)
- self.wait(seconds)
- Rectangle(...), Circle(...), Line(...), Arrow(...), VGroup(...)

Never invent animation names. self.play() may ONLY contain the animation functions listed above — nothing else.

Return ONLY the complete Python file, wrapped in a single ```python code fence. Do not add any explanation before or after the code fence.
"""


def build_prompt_equation(step, scene_name):
    return f"""Write a complete Manim Community Edition Python file.
{COMMON_RULES.format(scene_name=scene_name)}
Goal: teach this step of a concept, showing a piece of math notation.
Narration: "{step['narration']}"
Notation to display: "{step.get('display') or ''}"

Requirements for construct():
- title = Text(narration, font_size=28), positioned .to_edge(UP), animated with self.play(Write(title))
- eq = MathTex(the notation), positioned .move_to(ORIGIN)
- self.play(Write(eq))
- self.wait(2)
"""


def build_prompt_highlight_text(step, scene_name):
    return f"""Write a complete Manim Community Edition Python file.
{COMMON_RULES.format(scene_name=scene_name)}
Goal: teach this step by showing a sentence or phrase clearly on screen.
Narration: "{step['narration']}"
Text to display: "{step.get('display') or ''}"

Requirements for construct():
- title = Text(narration, font_size=26), .to_edge(UP), self.play(Write(title))
- body = Text(the text to display, font_size=36), .move_to(ORIGIN)
- self.play(Write(body))
- self.wait(2)
"""


def build_prompt_generic(step, scene_name):
    return f"""Write a complete Manim Community Edition Python file.
{COMMON_RULES.format(scene_name=scene_name)}
Goal: visually teach this step of a concept to a student. Keep the animation simple and clear given the limited allowed methods.
Narration: "{step['narration']}"
Content to display, if any: "{step.get('display') or ''}"
Suggested visual style: {step.get('visual_hint') or 'none'}

Requirements for construct():
- Show a title Text with the narration at the top, animated in
- If there is content to display, show it centered on screen using Text or MathTex as appropriate, animated in
- Keep it to 2-4 animation calls total
- self.wait(1) between animations so it's readable
"""


PROMPT_BUILDERS = {
    "equation": build_prompt_equation,
    "highlight_text": build_prompt_highlight_text,
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