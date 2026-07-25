from manim import *

class HelloWorld(Scene):
    def construct(self):
        text = Text("Hello World", font_size = 144)
        self.add(text)
        
class MarkupTest(Scene):
    def construct(self):
        text = MarkupText(
            f'<span underline="double" underline_color="green">double green underline</span> in red text<span fgcolor="{YELLOW}"> except this</span>',
            color=RED,
            font_size=34
        )
        self.add(text)

# We use Latex for Equations

class HelloLaTeX(Scene):
    def construct(self):
        tex = Tex(r"\LaTeX", font_size=144)
        self.add(tex)
        
class MathTeXDemo(Scene):
    def construct(self):
        rtarrow0 = MathTex(r"{y = e^x}", font_size=96)
        rtarrow1 = Tex(r"${dy/dx = e^x}$", font_size=96)

        self.add(VGroup(rtarrow0, rtarrow1).arrange(DOWN))
        
class Derivates(Scene):
    def construct(self):        
        equation = MathTex(r"y = e^x", font_size=96)
        derivate = MathTex(r"\frac{dy}{dx} = e^x", font_size=96)
        self.add(VGroup(equation, derivate).arrange(DOWN))
        
class LaTeXAlignEnvironment(Scene):
    def construct(self):
        tex = MathTex(r'f(x) &= (x+1).(x+2)\\ &= {x.(x+1) + 2.(x+1)} \\ &= {x^2 + x.1 + 2.x + 2.1}\\ &= {x^2 + 3x + 2}', font_size = 88)
        self.add(tex)