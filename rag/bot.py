"""Консольный (REPL) интерфейс RAG-бота.

Запуск:
    RAG_LLM_BACKEND=openai OPENAI_API_KEY=... python -m rag.bot
    RAG_LLM_BACKEND=ollama python -m rag.bot
"""
from dotenv import load_dotenv

load_dotenv()

from rag.pipeline import RAGPipeline


def main() -> None:
    print("RAG-бот QuantumForge. Введите вопрос (пустая строка — выход).")
    pipeline = RAGPipeline()
    while True:
        try:
            question = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not question:
            break
        result = pipeline.answer(question)
        print(f"\n{result['answer']}")
        print(f"\nИсточники: {', '.join(result['sources'])}")


if __name__ == "__main__":
    main()
