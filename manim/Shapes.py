from manim import *

class CircleToSquare(Scene):
    def construct(self):
        title = Text("A Random Circle is now a Square", font_size=36).to_edge(UP)
        self.play(Write(title))
        self.wait(1)

        circle = Circle()
        circle.set_fill(PINK, opacity=0.5)
        
        square = Square()
        square.set_fill(RED, opacity=0.5)
        square.rotate(PI/4)
        
        self.play(FadeIn(circle))
        self.play(Transform(circle, square))
        self.play(FadeOut(square))
        
        self.wait(2)
        
class AnimatedSquareToCircle(Scene):
    def construct(self):
        circle = Circle()  # create a circle
        
        square = Square()  # create a square
        square.set_fill(RED, opacity=1)

        self.play(Create(square))  # show the square on screen
        self.play(square.animate.rotate(PI / 4))  # rotate the square
        self.play(Transform(square, circle))  # transform the square into a circle
        self.play(
            circle.animate.set_fill(PINK, opacity=0.5)
        )  # color the circle on screen
        
class DifferentRotations(Scene):
    def construct(self):
        left_square = Square(color=BLUE, fill_opacity=0.7).shift(2 * LEFT)
        right_square = Square(color=GREEN, fill_opacity=0.7).shift(2 * RIGHT)
        self.play(
            left_square.animate.rotate(PI), Rotate(right_square, angle=PI), run_time=2
        )
        self.wait()       