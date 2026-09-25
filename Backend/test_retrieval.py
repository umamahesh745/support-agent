import time
from rag.retriever import retrieve

# (question, expected file, expected section)
TESTS = [
    ("Can I return a product after 10 days?", "returns_policy.md", "Return Window"),
    ("I received a damaged product, what should I do?", "returns_policy.md", "Damaged or Wrong Product"),
    ("How long does a UPI refund take?", "refund_policy.md", "Refund Timelines"),
    ("What does refund status approved mean?", "refund_policy.md", "Refund Status Meaning"),
    ("Is delivery free?", "shipping_policy.md", "Delivery Charges"),
    ("Can I change my delivery address after shipping?", "shipping_policy.md", "Changing the Delivery Address"),
    ("Can I cancel my order after it is shipped?", "cancellation_policy.md", "When You Can Cancel"),
    ("Is there any extra charge for cash on delivery?", "payment_policy.md", "Cash on Delivery"),
    ("Money was deducted but my order is not confirmed", "payment_policy.md", "Payment Failures"),
    ("What is the warranty on the smartwatch?", "warranty_policy.md", "Warranty Period by Product"),
    ("How do I reset my password?", "account_privacy.md", "Forgot Password"),
    ("I want to talk to a human agent", "faq_contact.md", "Contacting a Human Agent"),
    # Multilingual
    ("నా రిఫండ్ ఎన్ని రోజుల్లో వస్తుంది?", "refund_policy.md", "Refund Timelines"),
    ("order cancel cheyyali ela?", "cancellation_policy.md", "How to Cancel"),
    ("क्या आप विदेश में डिलीवरी करते हैं?", "faq_contact.md", "Do You Deliver Internationally"),
]

# Documents lo answer leni questions
OUT_OF_SCOPE = [
    "What is the capital of France?",
    "Can you recommend a good movie?",
    "What is your office address in Mumbai?",
]

hit1 = hit3 = 0
times = []
retrieve("warm up")  # model load time ni measure lo kalapakunda

print(f"{'Result':<8}{'Top dist':<10}{'Question'}")
for q, src, sec in TESTS:
    t = time.time()
    results = retrieve(q, k=3)
    times.append(time.time() - t)

    matches = [r["source"] == src and r["section"] == sec for r in results]
    if matches[0]:
        hit1 += 1
        status = "HIT@1"
    elif any(matches):
        status = "HIT@3"
    else:
        status = "MISS"
    hit3 += any(matches)

    print(f"{status:<8}{results[0]['distance']:<10}{q}")
    if status == "MISS":
        print(f"{'':<18}got: {results[0]['source']} > {results[0]['section']}")

n = len(TESTS)
print(f"\nHit@1: {hit1}/{n} ({hit1 / n:.0%})   Hit@3: {hit3}/{n} ({hit3 / n:.0%})")
print(f"Avg retrieval time: {sum(times) / n * 1000:.0f} ms")

print("\nOut-of-scope questions (top distance):")
for q in OUT_OF_SCOPE:
    r = retrieve(q, k=1)[0]
    print(f"  {r['distance']:<8}{q}")