FROM python:3.11-slim

# Установка зависимостей
RUN pip install --no-cache-dir \
    mlflow==2.8.0 \
    psycopg2-binary==2.9.9 \
    boto3==1.34.0

# Создание директории для артефактов
RUN mkdir -p /mlflow/artifacts

# Открываем порт
EXPOSE 5000

# Команда запуска (будет переопределена в docker-compose)
CMD ["mlflow", "server", "--host", "0.0.0.0", "--port", "5000"]