import time
from rag.qa import answer

QUESTIONS = [
    "Can I return a product after 10 days?",
    "How long does a UPI refund take?",
    "Is there any extra charge for cash on delivery?",
    "order cancel cheyyali ela?",
    "నా రిఫండ్ ఎన్ని రోజుల్లో వస్తుంది?",
    "What is the capital of France?",
]

for q in QUESTIONS:
    t = time.time()
    result = answer(q)
    print(f"\nQ: {q}")
    print(f"A: {result['answer']}")
    print(f"Sources: {result['sources'] or 'none'}")
    print(f"Time: {time.time() - t:.1f} sec")