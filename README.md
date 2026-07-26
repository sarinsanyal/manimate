# Manimate (PDF → Manim Explainer Video)

Upload a PDF on any topic (math, physics, English, history — anything) and get back a narrated Manim video that walks through the content step by step.

Runs fully local using [Ollama](https://ollama.com) — no paid LLM API required.

## Overview

1. **Extract** — pull text, equations, and figures out of the uploaded PDF.
2. **Segment** — split the extracted content into discrete problems/topics.
3. **Solve** — an LLM works through each problem and outputs structured, step-by-step reasoning (narration + what to visualize).
4. **Generate code** — a code-focused LLM turns each step into a Manim scene.
5. **Render** — run the generated code through Manim; if it fails, feed the error back to the LLM and retry.
6. **Narrate & assemble** — add synced voiceover (TTS) and stitch everything into a final video.

## Extract + Segment plan (in progress)

- **Extraction is text-only for v1.** PyMuPDF (`fitz`) pulls raw text from the PDF. Diagrams/images in the source PDF are not extracted or reproduced — the existing pipeline already assigns its own `visual_hint` per step and generates an original Manim visual from scratch, so source figures only need to inform the model conceptually, not be extracted pixel-for-pixel. Literal source-diagram reproduction is a possible future feature, not v1 scope.
- **Segmentation is LLM-based, not heading/font-size heuristics.** A new `segment_topics` node reads the full extracted text in one call and splits it into a list of topic strings. Heading detection via font size is unreliable across differently-formatted PDFs, and an LLM call is more robust and consistent with the rest of the pipeline's design.
- **Graph shape:**

extract_pdf → segment_topics → [explain_topic → verify_steps → generate_code → render_sandbox] (loop per topic)

  No changes needed to the four existing nodes — `segment_topics` just feeds topic strings into the same pipeline that's already been built and debugged, once per topic.

## Notes to Self:

1. Manim can generate videos of various resolutions:

```bash
manim -pql file.py SceneName # Low Res(854x480 15FPS)

manim -pqm file.py SceneName # Medium(1280x720 30FPS)

manim -pqh file.py SceneName # High(1920x1080 60FPS)

manim -pqp file.py SceneName # 2k(2560x1440 60FPS)

manim -pqk file.py SceneName # 4k(3840x2160 60FPS)

# Removing the -p part doesn't do the autoplay when we run the code.
```

Hence we can put these options of generation in the app, asking if we want the video in Low Res, Medium Res, High Res, or 2K, 4K res or more.



## Tech stack

| Stage | Tool |
|---|---|
| PDF text extraction | PyMuPDF / pdfplumber |
| Math OCR (equations) | Mathpix API or Nougat / pix2tex |
| Reasoning + solving | Ollama — `qwen2.5:7b` |
| Manim code generation | Ollama — `qwen2.5-coder:7b` |
| Animation rendering | [Manim Community Edition](https://www.manim.community/) |
| Narration / TTS | [manim-voiceover](https://github.com/ManimCommunity/manim-voiceover) |
| Video assembly | ffmpeg |

## Setup

```bash
# 1. Install Ollama and pull models
ollama pull qwen2.5:7b
ollama pull qwen2.5-coder:7b

# 2. Install Python dependencies
pip install manim openai pymupdf

# 3. Install ffmpeg + a LaTeX distro (needed for Manim's math rendering)
# Windows: https://www.ffmpeg.org and https://miktex.org
# Mac: brew install ffmpeg && brew install --cask mactex
# Ubuntu/Debian: sudo apt install ffmpeg texlive texlive-latex-extra

# 4. Sanity checks
ollama run qwen2.5:7b "What is 2+2?"
manim -pql test_scene.py SolveEquation
```

## Notes on local models

Local 7B-class models are weaker than paid frontier models at multi-step math reasoning and first-try correct code. To keep this workable:

- Solution steps are cross-checked numerically with `sympy` where possible before being passed to code generation.
- Manim code generation is constrained to a small library of reusable scene templates (equation morph, graph plot, geometric construction, text highlight) rather than fully free-form code.
- Failed renders are retried automatically (error fed back to the model), capped at 3 attempts.

## License

TBD
