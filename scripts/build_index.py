"""Строит векторный индекс FAISS по базе знаний.

Читает knowledge_base/*.md, режет на чанки, считает эмбеддинги локальной
моделью Sentence-Transformers и сохраняет индекс FAISS с метаданными.

Запуск:
    python scripts/build_index.py
"""
import time
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

BASE = Path(__file__).resolve().parent.parent
KB_DIR = BASE / "knowledge_base"
INDEX_DIR = BASE / "index"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 150


def load_documents() -> list:
    documents = []
    for path in sorted(KB_DIR.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        title = text.splitlines()[0].lstrip("# ").strip()
        category = path.name.split("__", 1)[0]
        documents.append(Document(
            page_content=text,
            metadata={"source": path.name, "title": title, "category": category},
        ))
    return documents


def main() -> None:
    documents = load_documents()
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE, chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_documents(documents)
    for index, chunk in enumerate(chunks):
        chunk.metadata["chunk_id"] = index

    embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)

    start = time.time()
    store = FAISS.from_documents(chunks, embeddings)
    elapsed = time.time() - start

    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    store.save_local(str(INDEX_DIR))

    print(f"Documents: {len(documents)}")
    print(f"Chunks: {len(chunks)}")
    print(f"Embedding model: {MODEL_NAME} (384-dim)")
    print(f"Index build time: {elapsed:.1f} s")
    print(f"Saved to: {INDEX_DIR}")


if __name__ == "__main__":
    main()
