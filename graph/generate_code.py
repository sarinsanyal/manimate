from langchain_ollama import ChatOllama
import re
from graph.state import GraphState


def generate_code_node(state: GraphState) -> GraphState:
    llm = ChatOllama(model="qwen2.5-coder:3b", temperature=0)

    step = state["steps"][0]  # for now, just handle the first step — we'll loop later

    prompt = f"""Write a complete Manim Community Edition Python file.

It must contain:
- The import line: from manim import *
- A class named GeneratedScene that inherits from Scene
- A construct(self) method with the animation logic

Goal: show this step of solving a math problem, with a bit of visual richness.
Narration: "{step['narration']}"
Equation before: "{step['from_expr']}"
Equation after: "{step['to_expr']}"

Requirements for construct():
- title = Text(narration, font_size=28), positioned with .to_edge(UP), animated in with self.play(Write(title))
- before_eq = MathTex(...), positioned with .move_to(ORIGIN) (the center — do NOT also put it at the top edge, that would overlap the title)
- Animate before_eq appearing with self.play(FadeIn(before_eq))
- after_eq = MathTex(...), same position as before_eq using after_eq.move_to(before_eq)
- Transform with self.play(TransformMatchingTex(before_eq, after_eq))
- After the transform, self.play(Indicate(after_eq, color=YELLOW)) — indicate the WHOLE equation, not a sub-part of it
- Do NOT index into a MathTex object's characters (e.g. no before_eq[0][1]) — only operate on whole MathTex objects

You may ONLY use these methods/functions inside construct() — do not invent any others:
- Text(...), MathTex(...)
- .to_edge(UP), .move_to(...), .next_to(other, direction)
- self.play(Write(x)), self.play(FadeIn(x)), self.play(FadeOut(x)), self.play(TransformMatchingTex(a, b)), self.play(Indicate(x, color=YELLOW))
- self.wait(seconds)

Return ONLY the complete Python file, wrapped in a single ```python code fence. Do not add any explanation before or after the code fence."""

    response = llm.invoke(prompt)
    code = response.content
    code = re.sub(r"^```python\s*|^```\s*|\s*```$", "", code.strip())

    return {**state, "manim_code": code}