from functools import lru_cache
from langchain_huggingface import HuggingFaceEmbeddings

MODEL_NAME = "Qwen/Qwen3-Embedding-0.6B"


@lru_cache(maxsize=1)
def get_embeddings():
    return HuggingFaceEmbeddings(
        model_name=MODEL_NAME,
        model_kwargs={"device": "cpu"},
        encode_kwargs={"normalize_embeddings": True},
        query_encode_kwargs={"normalize_embeddings": True, "prompt_name": "query"},
    )