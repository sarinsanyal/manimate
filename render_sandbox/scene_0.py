from manim import *

class Step1Scene(Scene):
    def construct(self):
        # Show the title at the top of the screen
        title = Text("Every complete sentence has two parts: a subject, who or what the sentence is about, and a predicate, what the subject does.")
        title.to_edge(UP)
        
        # Display the title
        self.play(Write(title))
        
        # Wait for 1 second to make it readable
        self.wait(1)