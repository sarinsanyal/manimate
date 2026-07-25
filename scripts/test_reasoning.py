from graph.build_graph import app
import time

problems = [
    "Solve for x: 2x + 3 = 7", #2
    "Solve for x: 3x - 5 = 10", #5 
    "Solve for x: x/2 + 1 = 4", #6
    "Solve for x: 5x + 2 = 3x + 10", #4
    "Solve for x: 4(x - 1) = 12", #4
]

if __name__ == "__main__":
    print("Reasoning Test Starts: \n")

    for problem in problems:
        start_time = time.perf_counter()

        try:
            result = app.invoke({"problem": problem, "steps": [], "raw_output": ""})
        except Exception as e:
            print(f"Problem given is: {problem}")
            print(f"  FAILED — {e}\n")
            continue

        end_time = time.perf_counter()
        exec_time = end_time - start_time

        print("Problem given is: ", problem, "\n")
        for i, step in enumerate(result["steps"], 1):
            status = "✓" if step.get("verified") else "✗"
            print(f"{i}. [{status}] {step['narration']}  |  {step['from_expr']} → {step['to_expr']}")

        overall = "ALL VERIFIED" if result.get("all_verified") else "SOME STEPS FAILED VERIFICATION"
        print(f"\n{overall}")
        print(f"Time taken is: {exec_time:.6f} seconds")
        print("-" * 60)