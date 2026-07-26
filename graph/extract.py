import re

def extract_code(raw: str) -> str:
    """Pull Python code out of an LLM response, preferring a markdown fence if present."""
    fence_match = re.search(r"```(?:python)?\s*(.*?)```", raw, re.DOTALL)
    if fence_match:
        return fence_match.group(1).strip()

    # No fence found — fall back to stripping any leading/trailing fence markers
    cleaned = re.sub(r"^```python\s*|^```\s*|\s*```$", "", raw.strip())
    return cleaned