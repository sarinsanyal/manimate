from graph.solve_problem import solve_node
from graph.generate_code import generate_code_node
import subprocess

if __name__ == "__main__":
    state = {"problem": "Solve for x: 2x + 3 = 7", "steps": [], "raw_output": ""}
    state = solve_node(state)
    state = generate_code_node(state)

    print("--- GENERATED CODE ---")
    print(state["manim_code"])

    with open("generated_scene.py", "w") as f:
        f.write(state["manim_code"])

    print("\n--- RENDERING ---")
    result = subprocess.run(
        ["manim", "-pqh", "generated_scene.py", "GeneratedScene"],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        print("Render succeeded.")
    else:
        print("Render FAILED:")
        print(result.stderr)