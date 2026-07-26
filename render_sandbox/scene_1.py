from manim import *

class Step2Scene(Scene):
    def construct(self):
        title = Text("In 'The dog runs fast', 'The dog' is the subject and 'runs fast' is the predicate.", font_size=26)
        title.to_edge(UP)

        body = Text("The dog runs fast", font_size=36)
        body.move_to(ORIGIN)

        self.play(Write(title))
        self.play(Write(body))
        self.wait(2)