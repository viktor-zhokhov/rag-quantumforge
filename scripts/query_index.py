"""Пример поиска по векторному индексу FAISS.

Запуск:
    python scripts/query_index.py "ваш запрос"
    python scripts/query_index.py          # прогонит демо-запросы
"""
import sys
from pathlib import Path

from langchain_community.vectorstores import FAISS

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

BASE = Path(__file__).resolve().parent.parent
INDEX_DIR = BASE / "index"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"

DEMO_QUERIES = [
    "Кто такой Kael Nerith?",
    "Что такое Void Core?",
    "Расскажи про Synth Flux",
]


def main() -> None:
    embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
    store = FAISS.load_local(
        str(INDEX_DIR), embeddings, allow_dangerous_deserialization=True,
    )

    queries = [" ".join(sys.argv[1:])] if len(sys.argv) > 1 else DEMO_QUERIES
    for query in queries:
        print(f"\n=== Запрос: {query}")
        results = store.similarity_search(query, k=3)
        for rank, doc in enumerate(results, 1):
            snippet = doc.page_content[:160].replace("\n", " ")
            print(f"  {rank}. [{doc.metadata['source']}] {snippet}...")


if __name__ == "__main__":
    main()
