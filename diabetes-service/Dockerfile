FROM python:3.10-slim

WORKDIR /app

# Копируем файлы зависимостей
COPY requirements.txt .


# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt
# RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

# Копируем код приложения и модель
COPY app/ ./app/
COPY models/ ./models/

# Создаем пользователя для безопасности
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Запускаем сервис
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]