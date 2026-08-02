import os

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "icons")

ICON_ALLOWLIST = [
    "sun", "leaf", "droplet", "cloud", "atom", "dna", "brain", "flame",
    "snowflake", "mountain", "tree-pine", "flask-conical", "microscope",
    "heart", "zap", "scale", "landmark", "swords", "crown", "map",
    "compass", "calculator", "function-square", "triangle", "square",
    "circle", "arrow-right", "trending-up", "users", "user", "globe",
    "factory", "wheat", "hammer", "scroll", "gavel", "coins", "building",
    "rocket", "thermometer", "wind", "cloud-rain", "book-open", "lightbulb",
]


def _icon_path(icon_name: str) -> str | None:
    path = os.path.join(ASSETS_DIR, f"{icon_name}.svg")
    return path if os.path.isfile(path) else None


def build_diagram_scene(scene_name: str, narration: str, stages: list[dict]) -> str:
    n = len(stages)
    x_positions = {
        2: [-3, 3],
        3: [-4.5, 0, 4.5],
    }.get(n, [i * 4.5 - (n - 1) * 2.25 for i in range(n)])

    lines = [
        "from manim import *",
        "",
        f"class {scene_name}(Scene):",
        "    def construct(self):",
        f'        title = Text("{narration}", font_size=26)',
        "        title.to_edge(UP, buff=0.6)",
        "        self.play(Write(title))",
        "",
    ]

    shape_vars = []
    for i, stage in enumerate(stages):
        icon_name = stage.get("icon") if stage.get("icon") in ICON_ALLOWLIST else None
        label = stage.get("label", "").replace('"', "'")
        x = x_positions[i]
        is_emphasized = (i == n // 2)
        color = "YELLOW" if is_emphasized else "BLUE_D"
        fill_opacity = "0.15" if is_emphasized else "0.12"
        var = f"shape{i+1}"
        shape_vars.append(var)

        icon_path = _icon_path(icon_name) if icon_name else None
        if icon_path:
            escaped_path = icon_path.replace("\\", "\\\\")
            lines.append(f'        {var}_circle = Circle(radius=1.0, stroke_width=3, color={color}, fill_color={color}, fill_opacity={fill_opacity}).move_to(RIGHT * {x})')
            lines.append(f'        {var}_icon = SVGMobject(r"{escaped_path}").set_stroke({color}, width=3).set_fill({color}, opacity=0.9)')
            lines.append(f'        {var}_icon.scale_to_fit_height(0.9).move_to({var}_circle.get_center())')
            lines.append(f'        {var} = VGroup({var}_circle, {var}_icon)')
        else:
            lines.append(f'        {var} = Circle(radius=1.0, stroke_width=3, color={color}, fill_color={color}, fill_opacity={fill_opacity}).move_to(RIGHT * {x})')

        lines.append(f'        {var}_label = Text("{label}", font_size=22, color=WHITE).next_to({var}, DOWN, buff=0.35)')
        lines.append(f'        self.play(Create({var}))')
        lines.append(f'        self.play(Write({var}_label))')
        lines.append("        self.wait(0.5)")

        if i > 0:
            prev = shape_vars[i - 1]
            arrow_line = f'        arrow{i} = Arrow({prev}.get_right(), {var}.get_left(), color=GREY_B, stroke_width=2, buff=0.15)'
            lines.insert(len(lines) - 4, arrow_line)
            lines.insert(len(lines) - 3, f'        self.play(Create(arrow{i}))')

        lines.append("")

    lines.append("        self.wait(2)")
    return "\n".join(lines)