import os
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()


def _gemini():
    from langchain_google_genai import ChatGoogleGenerativeAI
    return ChatGoogleGenerativeAI(model=os.getenv("GEMINI_MODEL"), max_retries=2, timeout=60)


def _groq():
    from langchain_groq import ChatGroq
    return ChatGroq(model=os.getenv("GROQ_MODEL"), temperature=0, max_retries=2, timeout=60)


@lru_cache(maxsize=1)
def get_llm():
    """Primary LLM (.env lo LLM_PROVIDER)."""
    return _groq() if os.getenv("LLM_PROVIDER", "gemini") == "groq" else _gemini()


@lru_cache(maxsize=1)
def get_backup_llm():
    """Primary fail aithe vade second LLM."""
    return _gemini() if os.getenv("LLM_PROVIDER", "gemini") == "groq" else _groq()