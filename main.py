from dotenv import load_dotenv
load_dotenv()

import argparse
import time
from graph.build_pdf_graph import pdf_app
from graph.build_graph import app


def run_topic(topic, topic_excerpt="", raw_pdf_text="", topics=None, pdf_path=None):
    start_time = time.perf_counter()

    initial_state = {
        "pdf_path": pdf_path,
        "raw_pdf_text": raw_pdf_text,
        "topics": topics or [],
        "topic": topic,
        "topic_excerpt": topic_excerpt,
        "steps": [], "raw_output": "", "all_verified": False,
        "scenes": [], "rendered_clips": [], "failed_scenes": [], "retry_count": 0,
    }

    try:
        result = app.invoke(initial_state)
    except Exception as e:
        print(f"Topic given is: {topic}")
        print(f"  FAILED — {e}\n")
        return None

    exec_time = time.perf_counter() - start_time

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

    return result


def main():
    parser = argparse.ArgumentParser(description="Manimate pipeline runner")
    parser.add_argument("--pdf", help="Path to a PDF to extract and segment into topics")
    parser.add_argument("--topic", help="Run a single hardcoded topic, skipping PDF extraction")
    args = parser.parse_args()

    if not args.pdf and not args.topic:
        parser.error("Provide either --pdf <path> or --topic \"<topic name>\"")

    if args.topic:
        run_topic(args.topic)
        return

    print("\nExtracting and segmenting PDF...\n")
    pdf_result = pdf_app.invoke({
        "pdf_path": args.pdf,
        "raw_pdf_text": "", "topics": [],
        "topic": "", "steps": [], "raw_output": "", "all_verified": False,
        "scenes": [], "rendered_clips": [], "failed_scenes": [], "retry_count": 0,
    })

    topics = pdf_result["topics"]
    print(f"\nRunning full pipeline for {len(topics)} topic(s) from PDF\n")

    for topic_info in topics:
        run_topic(
            topic_info["title"],
            topic_excerpt=topic_info.get("excerpt", ""),
            raw_pdf_text=pdf_result["raw_pdf_text"],
            topics=topics,
            pdf_path=args.pdf,
        )


if __name__ == "__main__":
    main()