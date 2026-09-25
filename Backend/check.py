import importlib, os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

for lib in ["torch","langchain","langgraph","sentence_transformers","chromadb","fastapi",
            "sqlalchemy","pymysql","faster_whisper","gtts","transformers","ragas"]:
    try: importlib.import_module(lib); print("OK     ", lib)
    except Exception as e: print("FAILED ", lib, e)

load_dotenv()
with create_engine(os.getenv("DATABASE_URL")).connect() as c:
    print("MySQL  ", c.execute(text("SELECT VERSION()")).scalar())

print("CHECK FILE RUNNING")