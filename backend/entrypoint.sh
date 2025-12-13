#!/bin/sh
set -e

# Ждем готовности базы данных
until python -c "import psycopg2; psycopg2.connect('${DATABASE_URL}')" 2>/dev/null; do
  echo "Waiting for database..."
  sleep 1
done

# Исправляем последовательность для users после создания демо-пользователя
python << EOF
from database.config.database import engine
from sqlalchemy import text

with engine.begin() as conn:
    try:
        # Пытаемся синхронизировать последовательность
        result = conn.execute(text("""
            SELECT setval('users_id_seq', COALESCE((SELECT MAX(id) FROM users), 1), true)
        """))
        print("Sequence synchronized for users table")
    except Exception as e:
        # Если последовательности нет, создаем и привязываем
        print(f"Sequence not found or error: {e}, creating...")
        try:
            conn.execute(text("CREATE SEQUENCE IF NOT EXISTS users_id_seq"))
            conn.execute(text("ALTER TABLE users ALTER COLUMN id SET DEFAULT nextval('users_id_seq')"))
            conn.execute(text("ALTER SEQUENCE users_id_seq OWNED BY users.id"))
            conn.execute(text("SELECT setval('users_id_seq', COALESCE((SELECT MAX(id) FROM users), 1), true)"))
            print("Sequence created and synchronized")
        except Exception as e2:
            print(f"Could not fix sequence: {e2}")
EOF

# Запускаем приложение
exec uvicorn backend.main:app --host 0.0.0.0 --port 8000

