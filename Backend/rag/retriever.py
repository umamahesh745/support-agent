from langchain_chroma import Chroma
from .embeddings import get_embeddings
from .ingest import CHROMA_DIR, COLLECTION

_store = None


def get_store():
    global _store
    if _store is None:
        _store = Chroma(
            collection_name=COLLECTION,
            embedding_function=get_embeddings(),
            persist_directory=str(CHROMA_DIR),
        )
    return _store


def retrieve(query: str, k: int = 3):
    results = get_store().similarity_search_with_score(query, k=k)
    return [
        {
            "content": doc.page_content,
            "source": doc.metadata["source"],
            "section": doc.metadata["section"],
            "distance": round(score, 3),
        }
        for doc, score in results
    ]