from graph.build_graph import app
import time

topics = [
    "Solve for x: 2x + 3 = 7",
    "The Water Cycle",
    "Subject and predicate in a sentence",
]

if __name__ == "__main__":
    print("\nFull Pipeline Test Starts: \n")

    for topic in topics:
        start_time = time.perf_counter()

        initial_state = {
            "topic": topic,
            "steps": [], "raw_output": "", "all_verified": False,
            "scenes": [], "rendered_clips": [], "failed_scenes": [], "retry_count": 0,
        }
        try:
            result = app.invoke(initial_state)
        except Exception as e:
            print(f"Topic given is: {topic}")
            print(f"  FAILED — {e}\n")
            continue

        end_time = time.perf_counter()
        exec_time = end_time - start_time

        print("Topic given is: ", topic, "\n")
        for i, step in enumerate(result["steps"], 1):
            status = "✓" if step.get("verified") else "✗"
            display = step.get("display") or ""
            hint = step.get("visual_hint") or "none"
            print(f"{i}. [{status}] ({hint}) {step['narration']}  |  {display}")

        overall = "ALL VERIFIED" if result.get("all_verified") else "SOME STEPS FAILED VERIFICATION"
        print(f"\n{overall}")
        print(f"Rendered clips: {len(result.get('rendered_clips', []))} / {len(result['steps'])}")
        print(f"Retry count: {result.get('retry_count', 0)}")
        if result.get("failed_scenes"):
            print(f"Still failing after retries: {[s['scene_name'] for s in result['failed_scenes']]}")
        print(f"Time taken is: {exec_time:.2f} seconds")
        print("-" * 60)