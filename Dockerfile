FROM python:3.11-slim

WORKDIR /app

# Копируем весь проект
COPY . .

# Устанавливаем зависимости
RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy psycopg2-binary python-dotenv passlib[bcrypt]

EXPOSE 8000

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]