from manim import *

class Step3Scene(Scene):
    def construct(self):
        title = Text("Condensation", color=BLUE).to_edge(UP)
        self.play(Write(title))
        
        content = MathTex(r"\text{Vapor rises and cools}", color=YELLOW).next_to(title, DOWN)
        self.play(FadeIn(content))
        
        self.wait(1)