from langchain_core.prompts import ChatPromptTemplate
from .retriever import retrieve
from .llm import get_llm

MAX_DISTANCE = 0.6  # retrieval test out-of-scope results batti adjust cheddam

SYSTEM_PROMPT = """You are ShopEasy's customer support assistant.
Answer ONLY using the policy context below.

Rules:
- If the context does not contain the answer, say you don't have that information and offer to connect the customer to a human agent.
- Never invent numbers, timelines, prices, or policies.
- Reply in the same language the customer used (English, Telugu, Hindi, or Telugu written in English letters).
- Keep answers short and friendly: 2 to 4 sentences.

Policy context:
{context}"""

prompt = ChatPromptTemplate.from_messages([
    ("system", SYSTEM_PROMPT),
    ("human", "{question}"),
])


def answer(question: str):
    chunks = [c for c in retrieve(question, k=3) if c["distance"] <= MAX_DISTANCE]

    if not chunks:
        return {
            "answer": "Sorry, I don't have information about that. I can connect you to a human agent if you'd like.",
            "sources": [],
        }

    context = "\n\n".join(f"[{c['source']} > {c['section']}]\n{c['content']}" for c in chunks)
    response = (prompt | get_llm()).invoke({"context": context, "question": question})

    return {
        "answer": response.text,
        "sources": sorted({f"{c['source']} > {c['section']}" for c in chunks}),
    }