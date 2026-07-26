from manim import *

class GeneratedScene(Scene):
    def construct(self):
        # Title of the scene
        title = Text("Subtract 3 from both sides", font_size=28)
        self.play(Write(title))

        # Equation before transformation
        before_eq = MathTex(r"2x + 3 = 7")
        before_eq.move_to(ORIGIN)

        # Animate the appearance of the equation
        self.play(FadeIn(before_eq))

        # Equation after transformation
        after_eq = MathTex(r"2x = 4")
        after_eq.move_to(before_eq)

        # Transform the equations
        self.play(TransformMatchingTex(before_eq, after_eq))

        # Indicate the entire equation
        self.play(Indicate(after_eq, color=YELLOW))