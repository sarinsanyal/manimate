from manim import *

class Step4Scene(Scene):
    def construct(self):
        # Show the title at the top of the screen
        title = Text("The water in the clouds falls as precipitation, either as rain or snow, which then flows back into oceans, lakes, rivers, and underground streams.")
        self.play(Write(title), run_time=2)
        
        # Display "Precipitation" centered on the screen
        precipitation_text = Text("Precipitation")
        precipitation_text.to_edge(UP)
        self.play(FadeIn(precipitation_text))
        
        # Wait for 1 second before ending the scene
        self.wait(1)