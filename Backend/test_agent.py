import time
from agent.graph import chat
from db.database import SessionLocal
from db.models import Order

with SessionLocal() as db:
    placed = db.query(Order).filter(Order.status == "placed").first()
    placed_id = placed.id if placed else 1002

CONVERSATIONS = {
    "memory-test": [
        "Hi",
        "What is the status of order 1024?",
        "Can I still return it?",
    ],
    "cancel-test": [
        f"Please cancel my order {placed_id}",
        "Yes, cancel it",
    ],
    "multi-tool": [
        "Order 1006 refund enti, eppudu vastundi?",
    ],
    "escalation": [
        "I am very angry, my order 1019 is still not delivered. I want to talk to a human!",
    ],
    "off-topic": [
        "Who won the cricket world cup?",
    ],
}

for thread_id, messages in CONVERSATIONS.items():
    print(f"\n{'=' * 20} {thread_id} {'=' * 20}")
    for msg in messages:
        start = time.time()
        reply, tools = chat(msg, thread_id)
        print(f"\nCustomer: {msg}")
        print(f"Tools:    {tools or 'none'}")
        print(f"Agent:    {reply}")
        print(f"({time.time() - start:.1f} sec)")
        time.sleep(3)  # free tier rate limit kosam