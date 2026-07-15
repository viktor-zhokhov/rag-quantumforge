# rag-quantumforge

Проектная работа 7 спринта Яндекс Практикума (архитектура ПО): RAG-бот для корпоративной базы знаний компании **QuantumForge Software**.

Бот отвечает на вопросы сотрудников по внутренней базе знаний, используя технологию **Retrieval-Augmented Generation (RAG)** и техники промптинга (Few-shot, Chain-of-Thought), а также защищён от prompt-инъекций.

## Структура репозитория

| Путь | Что внутри | Задание |
|---|---|---|
| `research/` | Исследование моделей, эмбеддингов, векторных БД и инфраструктуры | Задание 1 |
| `knowledge_base/` | База знаний: 30+ документов с вымышленными терминами | Задание 2 |
| `scripts/` | Скрипты подмены терминов и построения индекса | Задания 2–3 |
| `rag/` | Модуль RAG-бота: пайплайн, промптинг, интерфейс | Задание 4 |
| `screenshots/` | Скрины демонстрации работы и защиты | Задание 5 |
| `Project_template.md` | Ответы и описание решений по всем заданиям | все |

## Запуск

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Подробности — в `Project_template.md`.

## Технологический стек

- Python 3.11
- LangChain
- FAISS (векторная БД)
- Sentence-Transformers / OpenAI Embeddings
- Docker + docker compose
