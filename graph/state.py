from typing import TypedDict, List, Literal, Optional

VisualHint = Literal[
    "equation", "graph", "number_line", "shape",
    "timeline", "diagram", "map", "comparison",
    "highlight_text", "tree", "none"
]

class Step(TypedDict):
    narration: str
    display: Optional[str]
    visual_hint: VisualHint

class TopicInfo(TypedDict):
    title: str
    excerpt: str

class GraphState(TypedDict):
    pdf_path: Optional[str]
    raw_pdf_text: Optional[str]
    topics: List[TopicInfo]      # was List[str]
    topic: str
    topic_excerpt: Optional[str] # new
    steps: List[Step]
    raw_output: str
    scenes: List[dict]
    rendered_clips: List[str]
    failed_scenes: List[dict]
    retry_count: int
    all_verified: bool