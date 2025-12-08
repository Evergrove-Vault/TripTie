FROM python:3.11-slim

WORKDIR /app

# Копируем ВЕСЬ проект
COPY . .

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y libpq-dev libffi-dev gcc && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir -r backend/requirements.txt

# Настраиваем Python путь
ENV PYTHONPATH=/app:$PYTHONPATH

EXPOSE 8000
WORKDIR /app/backend
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]