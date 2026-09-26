from contextlib import asynccontextmanager
from datetime import datetime, timedelta

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from sqlalchemy import func

from agent.graph import chat
from db.database import SessionLocal
from db.models import Conversation, Customer, Message, Ticket
from rag.retriever import retrieve


@asynccontextmanager
async def lifespan(app: FastAPI):
    retrieve("warm up")  # Qwen model + ChromaDB server start lone load, first user wait avvakunda
    yield


app = FastAPI(title="ShopEasy Support Agent API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React dev server
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------- Request / Response formats ----------

class ChatRequest(BaseModel):
    message: str = Field(min_length=1, max_length=2000)
    conversation_id: int | None = None


class ChatResponse(BaseModel):
    conversation_id: int
    reply: str
    tools_used: list[str]
    escalated: bool


# ---------- Endpoints ----------

@app.get("/api/health")
def health():
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
def chat_endpoint(req: ChatRequest):
    # 1. Conversation create / load + user message save
    with SessionLocal() as db:
        if req.conversation_id:
            conv = db.get(Conversation, req.conversation_id)
            if not conv:
                raise HTTPException(status_code=404, detail="Conversation not found")
        else:
            conv = Conversation()
            db.add(conv)
            db.commit()
            db.refresh(conv)
        conv_id = conv.id
        db.add(Message(conversation_id=conv_id, role="user", content=req.message))
        db.commit()

    # 2. Agent call (same conversation ki same thread_id → memory)
    try:
        reply, tools = chat(req.message, thread_id=f"conv-{conv_id}")
    except Exception as e:
        print("Agent error:", repr(e))
        reply, tools = "Sorry, I'm having trouble right now. Please try again in a moment.", []

    # 3. Agent reply save + escalation mark
    with SessionLocal() as db:
        conv = db.get(Conversation, conv_id)
        if "create_ticket" in tools:
            conv.escalated = True
        db.add(Message(conversation_id=conv_id, role="agent", content=reply))
        db.commit()
        escalated = conv.escalated

    return ChatResponse(conversation_id=conv_id, reply=reply, tools_used=tools, escalated=escalated)


@app.get("/api/conversations/{conv_id}/messages")
def get_messages(conv_id: int):
    with SessionLocal() as db:
        msgs = (
            db.query(Message)
            .filter(Message.conversation_id == conv_id)
            .order_by(Message.id)
            .all()
        )
        return [
            {"role": m.role, "content": m.content, "created_at": m.created_at.isoformat()}
            for m in msgs
        ]


@app.get("/api/stats")
def get_stats():
    with SessionLocal() as db:
        total = db.query(func.count(Conversation.id)).scalar()
        escalated = db.query(func.count(Conversation.id)).filter(Conversation.escalated.is_(True)).scalar()
        messages = db.query(func.count(Message.id)).scalar()
        open_tickets = db.query(func.count(Ticket.id)).filter(Ticket.status != "closed").scalar()

        # Last 7 days conversations (chart kosam)
        start = (datetime.now() - timedelta(days=6)).replace(hour=0, minute=0, second=0, microsecond=0)
        rows = (
            db.query(func.date(Conversation.started_at), func.count(Conversation.id))
            .filter(Conversation.started_at >= start)
            .group_by(func.date(Conversation.started_at))
            .all()
        )
        per_day = {str(day): count for day, count in rows}
        days = [(start + timedelta(days=i)).date() for i in range(7)]

        return {
            "total_conversations": total,
            "total_messages": messages,
            "escalated_conversations": escalated,
            "resolution_rate": round((total - escalated) / total * 100, 1) if total else 0,
            "open_tickets": open_tickets,
            "conversations_per_day": [
                {"date": d.strftime("%d %b"), "count": per_day.get(str(d), 0)} for d in days
            ],
        }


@app.get("/api/tickets")
def get_tickets(limit: int = 20):
    with SessionLocal() as db:
        rows = (
            db.query(Ticket, Customer.name)
            .outerjoin(Customer, Ticket.customer_id == Customer.id)
            .order_by(Ticket.created_at.desc())
            .limit(limit)
            .all()
        )
        return [
            {
                "id": t.id,
                "customer": name or "Guest",
                "issue": t.issue,
                "priority": t.priority,
                "status": t.status,
                "created_at": t.created_at.strftime("%d %b %Y, %I:%M %p"),
            }
            for t, name in rows
        ]