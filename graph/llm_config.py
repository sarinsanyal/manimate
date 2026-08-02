import os
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq

BACKEND = os.environ.get("LLM_BACKEND", "ollama")  # "ollama" or "groq"

REASONING_MODEL_OLLAMA = "qwen2.5:1.5b"
CODER_MODEL_OLLAMA = "qwen2.5-coder:3b"

REASONING_MODEL_GROQ = "llama-3.3-70b-versatile"
CODER_MODEL_GROQ = "openai/gpt-oss-120b"

def get_reasoning_llm(**kwargs):
    if BACKEND == "groq":
        return ChatGroq(model=REASONING_MODEL_GROQ, temperature=0, **kwargs)
    return ChatOllama(model=REASONING_MODEL_OLLAMA, temperature=0, **kwargs)


def get_coder_llm(**kwargs):
    if BACKEND == "groq":
        return ChatGroq(model=CODER_MODEL_GROQ, temperature=0, **kwargs)
    return ChatOllama(model=CODER_MODEL_OLLAMA, temperature=0, **kwargs)