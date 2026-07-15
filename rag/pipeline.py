"""RAG-пайплайн: запрос → поиск чанков → промпт (few-shot + CoT) → ответ LLM.

Логика «под капотом» (без готовой RetrievalQA), чтобы было видно каждый шаг:
1. запрос пользователя превращаем в эмбеддинг тем же энкодером, что и индекс;
2. ищем ближайшие чанки в FAISS;
3. собираем промпт с найденными фрагментами;
4. отправляем в LLM и возвращаем ответ вместе с источниками.
"""
from pathlib import Path

from langchain_community.vectorstores import FAISS

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

from rag.llm import get_llm
from rag.prompts import build_messages
from rag.defense import sanitize_context, guard_output

BASE = Path(__file__).resolve().parent.parent
INDEX_DIR = BASE / "index"
MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"


class RAGPipeline:
    def __init__(self, top_k: int = 4, index_dir: Path = INDEX_DIR, defense: bool = True) -> None:
        self.top_k = top_k
        self.defense = defense
        self.embeddings = HuggingFaceEmbeddings(model_name=MODEL_NAME)
        self.store = FAISS.load_local(
            str(index_dir), self.embeddings, allow_dangerous_deserialization=True,
        )
        self.llm = get_llm()

    def retrieve(self, question: str) -> list:
        return self.store.similarity_search(question, k=self.top_k)

    def build_context(self, docs: list) -> str:
        blocks = []
        for doc in docs:
            source = doc.metadata.get("source", "unknown")
            content = doc.page_content
            if self.defense:
                content = sanitize_context(content)
            blocks.append(f"[{source}]\n{content}")
        return "\n\n".join(blocks)

    def answer(self, question: str) -> dict:
        docs = self.retrieve(question)
        context = self.build_context(docs)
        messages = build_messages(context, question)
        response = self.llm.invoke(messages)
        answer = response.content
        if self.defense:
            answer = guard_output(answer)
        sources = sorted({doc.metadata.get("source", "unknown") for doc in docs})
        return {"answer": answer, "sources": sources}
