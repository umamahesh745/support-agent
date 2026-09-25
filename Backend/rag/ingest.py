import shutil
import time
from pathlib import Path

from langchain_chroma import Chroma
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from .embeddings import get_embeddings

BASE_DIR = Path(__file__).resolve().parent.parent
POLICY_DIR = BASE_DIR / "data" / "policies"
CHROMA_DIR = BASE_DIR / "chroma_db"
COLLECTION = "shopeasy_policies"

header_splitter = MarkdownHeaderTextSplitter(
    headers_to_split_on=[("#", "title"), ("##", "section")]
)
text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)


def load_chunks():
    chunks, ids = [], []
    for path in sorted(POLICY_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        sections = header_splitter.split_text(text)
        docs = text_splitter.split_documents(sections)

        for i, doc in enumerate(docs):
            title = doc.metadata.get("title", path.stem)
            section = doc.metadata.get("section", "Introduction")
            # Heading ni chunk mundu add chestunnam, search accuracy ki help avutundi
            doc.page_content = f"{title} > {section}\n{doc.page_content}"
            doc.metadata.update({"source": path.name, "title": title, "section": section})
            chunks.append(doc)
            ids.append(f"{path.stem}-{i}")
    return chunks, ids


def ingest():
    start = time.time()
    chunks, ids = load_chunks()
    if not chunks:
        print(f"No documents found in {POLICY_DIR}")
        return

    if CHROMA_DIR.exists():
        shutil.rmtree(CHROMA_DIR)  # prathi sari fresh index

    store = Chroma.from_documents(
        documents=chunks,
        embedding=get_embeddings(),
        ids=ids,
        collection_name=COLLECTION,
        persist_directory=str(CHROMA_DIR),
        collection_metadata={"hnsw:space": "cosine"},
    )

    files = len({c.metadata["source"] for c in chunks})
    avg = sum(len(c.page_content) for c in chunks) // len(chunks)
    print(f"Files: {files} | Chunks: {len(chunks)} | Avg chunk size: {avg} chars")
    print(f"Indexing time: {time.time() - start:.1f} sec")

    print("\nSanity check: 'Can I return a product after 10 days?'")
    for doc, dist in store.similarity_search_with_score("Can I return a product after 10 days?", k=3):
        print(f"  {dist:.3f}  {doc.metadata['source']} > {doc.metadata['section']}")


if __name__ == "__main__":
    ingest()