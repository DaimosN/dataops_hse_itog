# Diabetes Prediction Service

ML сервис для предсказания прогрессии диабета на основе данных пациента.

## Установка и запуск

### Предварительные требования
- Docker и Docker Compose
- Python 3.9+ (для локальной разработки)

### Запуск через Docker Compose

```bash
# Клонировать репозиторий
git clone <repository-url>
cd ml-service

# Создать директорию для модели
mkdir -p models

# Обучить модель (см. инструкции ниже)
# ... скопировать модель в models/diabetes_model.joblib

# Запустить сервисы
docker-compose up --build