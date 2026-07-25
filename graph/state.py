from typing import TypedDict, List

class GraphState(TypedDict):
    problem: str
    steps: List[dict]
    raw_output: str
    all_verified: bool