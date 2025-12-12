FROM python:3.11-slim

# Рабочая директория - папка backend
WORKDIR /app/backend

# Устанавливаем зависимости
RUN apt-get update && apt-get install -y libpq-dev gcc && rm -rf /var/lib/apt/lists/*
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем ВЕСЬ проект в /app
COPY . /app

# Настраиваем Python путь
ENV PYTHONPATH=/app:$PYTHONPATH

EXPOSE 8000

# Запускаем скрипты из корня и сервер из backend
CMD ["sh", "-c", "echo 'Waiting for DB...' && sleep 5 && echo 'Running DB scripts...' && python /app/database/scripts/init_db.py && python /app/database/scripts/seed_data.py && echo 'Starting server...' && uvicorn main:app --host 0.0.0.0 --port 8000"]