FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONPATH=/app

# Бот с встроенным (in-process) индексом FAISS. Модель эмбеддингов
# подтягивается при первом запуске.
CMD ["python", "-m", "rag.bot"]
