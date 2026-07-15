"""Фабрика LLM-бэкенда: OpenAI (по умолчанию) или локальная Ollama.

Выбор через переменную окружения RAG_LLM_BACKEND (openai | ollama).
Соответствует рекомендации Задания 1: облачный GPT-4o-mini для обычных
запросов + локальная модель для конфиденциальных данных.
"""
import os


def get_llm():
    backend = os.getenv("RAG_LLM_BACKEND", "openai").lower()

    if backend == "ollama":
        from langchain_ollama import ChatOllama
        model = os.getenv("RAG_OLLAMA_MODEL", "llama3.1")
        return ChatOllama(model=model, temperature=0)

    from langchain_openai import ChatOpenAI
    model = os.getenv("RAG_OPENAI_MODEL", "gpt-4o-mini")
    return ChatOpenAI(model=model, temperature=0)
