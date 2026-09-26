import time
from rag.llm import get_llm

llm = get_llm()
print("Model:", llm.model_name if hasattr(llm, "model_name") else llm)

for i in range(3):
    t = time.time()
    r = llm.invoke("Reply with one word: hello")
    print(f"{i + 1}. {r.text!r}  {time.time() - t:.2f} sec")