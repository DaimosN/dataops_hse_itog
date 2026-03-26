from fastapi import FastAPI, HTTPException
import numpy as np
from mlflow import MlflowClient
import random
import os
import time
from starlette_exporter import PrometheusMiddleware, handle_metrics
from prometheus_client import Counter, Histogram, Gauge
import logging

from app.schemas import PatientData, PredictionResponse
from app.model import model_loader

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создаем приложение FastAPI
app = FastAPI(title="Diabetes Prediction Service")

# Добавляем Prometheus middleware для сбора метрик HTTP запросов
app.add_middleware(
    PrometheusMiddleware,
    app_name="diabetes_service",
    prefix="diabetes",
    group_paths=True,  # Группируем похожие пути
    skip_paths=["/metrics", "/health"],  # Не собираем метрики для этих путей
    buckets=[0.1, 0.25, 0.5, 1, 2.5, 5, 10]  # Специальные buckets для гистограммы
)

# Добавляем эндпоинт для метрик
app.add_route("/metrics", handle_metrics)

# Создаем кастомные метрики
# Счетчик для предсказаний по методам API
predictions_by_endpoint = Counter(
    'diabetes_predictions_by_endpoint_total',
    'Total number of predictions by endpoint',
    ['endpoint', 'model_version', 'status']
)

# Счетчик для методов MLflow
mlflow_methods_total = Counter(
    'diabetes_mlflow_methods_total',
    'Total number of MLflow method calls',
    ['method_name', 'status']
)

# Гистограмма для времени выполнения MLflow методов
mlflow_method_duration = Histogram(
    'diabetes_mlflow_method_duration_seconds',
    'Duration of MLflow method calls in seconds',
    ['method_name'],
    buckets=[0.05, 0.1, 0.25, 0.5, 1, 2.5, 5]
)

# Gauge для отслеживания состояния модели
model_info = Gauge(
    'diabetes_model_info',
    'Information about loaded model',
    ['model_name', 'model_version', 'source']
)

# Gauge для статуса MLflow
mlflow_status = Gauge(
    'diabetes_mlflow_status',
    'MLflow connection status (1=up, 0=down)'
)


@app.on_event("startup")
async def startup_event():
    """Действия при запуске приложения"""
    logger.info("Starting up Diabetes Prediction Service...")

    # Загружаем модель при старте
    try:
        model_loader.load_model()
        model_info.labels(
            model_name="diabetes_model",
            model_version=os.getenv("MODEL_VERSION", "local"),
            source="local"
        ).set(1)
        logger.info("✅ Model loaded successfully")
    except Exception as e:
        logger.error(f"❌ Error loading model: {e}")
        model_info.labels(
            model_name="diabetes_model",
            model_version="unknown",
            source="error"
        ).set(0)


@app.get("/")
async def root():
    """Корневой эндпоинт"""
    return {
        "message": "Diabetes Prediction Service",
        "version": os.getenv("MODEL_VERSION", "1.0.0"),
        "endpoints": {
            "/health": "Health check",
            "/metrics": "Prometheus metrics",
            "/mlflow/status": "MLflow status",
            "/api/v1/predict": "Make prediction"
        }
    }


@app.get("/health")
async def health():
    """Проверка здоровья сервиса и доступности модели"""
    try:
        model_loader.load_model()
        return {
            "status": "healthy",
            "model_loaded": True,
            "model_version": os.getenv("MODEL_VERSION", "local")
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "model_loaded": False,
            "error": str(e)
        }


@app.post("/api/v1/predict", response_model=PredictionResponse)
async def predict(data: PatientData):
    """
    Предсказание прогрессии диабета на основе данных пациента
    """
    endpoint = "/api/v1/predict"
    model_version = os.getenv("MODEL_VERSION", "local")

    try:
        # Преобразуем данные в формат для модели
        features = [
            data.age, data.sex, data.bmi, data.bp,
            data.s1, data.s2, data.s3, data.s4, data.s5, data.s6
        ]

        # Получаем предсказание
        prediction = model_loader.predict(features)

        # Обновляем метрики
        predictions_by_endpoint.labels(
            endpoint=endpoint,
            model_version=model_version,
            status="success"
        ).inc()

        logger.info(f"✅ Prediction successful: {prediction}")

        return {"predict": round(prediction, 2)}

    except Exception as e:
        predictions_by_endpoint.labels(
            endpoint=endpoint,
            model_version=model_version,
            status="error"
        ).inc()
        logger.error(f"❌ Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Ошибка при предсказании: {str(e)}")


def track_mlflow_method(method_name):
    """Декоратор для отслеживания MLflow методов"""

    def decorator(func):
        def wrapper(*args, **kwargs):
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                mlflow_methods_total.labels(
                    method_name=method_name,
                    status="success"
                ).inc()
                return result
            except Exception as e:
                mlflow_methods_total.labels(
                    method_name=method_name,
                    status="error"
                ).inc()
                raise e
            finally:
                duration = time.time() - start_time
                mlflow_method_duration.labels(
                    method_name=method_name
                ).observe(duration)

        return wrapper

    return decorator


@app.get("/mlflow/status")
async def mlflow_status():
    """Детальная проверка статуса MLflow с отслеживанием метрик"""
    status = {
        "tracking_uri": os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000"),
        "mlflow_available": False,
        "model_in_registry": False,
        "local_model_exists": False,
        "methods_calls": {},
        "errors": []
    }

    # Проверяем локальную модель
    from pathlib import Path
    local_model = Path(__file__).parent.parent / "models" / "diabetes_model.joblib"
    status["local_model_exists"] = local_model.exists()

    # Проверяем MLflow с отслеживанием методов
    try:
        import requests

        # Метод: список экспериментов
        start_time = time.time()
        response = requests.get(
            f"{status['tracking_uri']}/api/2.0/mlflow/experiments/list",
            timeout=5,
            headers={"Host": "mlflow"}
        )

        mlflow_method_duration.labels(
            method_name="list_experiments"
        ).observe(time.time() - start_time)

        if response.status_code == 200:
            mlflow_methods_total.labels(
                method_name="list_experiments",
                status="success"
            ).inc()

            status["mlflow_available"] = True
            status["experiments"] = len(response.json().get("experiments", []))
            mlflow_status.set(1)

            # Проверяем наличие модели в registry
            try:
                start_time = time.time()
                client = MlflowClient(tracking_uri=status['tracking_uri'])
                model_versions = client.get_latest_versions("diabetes_model")

                mlflow_method_duration.labels(
                    method_name="get_latest_versions"
                ).observe(time.time() - start_time)

                mlflow_methods_total.labels(
                    method_name="get_latest_versions",
                    status="success"
                ).inc()

                status["model_in_registry"] = len(model_versions) > 0
                if model_versions:
                    status["latest_model_version"] = model_versions[0].version

            except Exception as e:
                mlflow_methods_total.labels(
                    method_name="get_latest_versions",
                    status="error"
                ).inc()
                status["errors"].append(f"Ошибка при проверке registry: {str(e)}")
        else:
            mlflow_methods_total.labels(
                method_name="list_experiments",
                status="error"
            ).inc()
            mlflow_status.set(0)
            status["errors"].append(f"HTTP {response.status_code}: {response.text}")

    except Exception as e:
        mlflow_methods_total.labels(
            method_name="list_experiments",
            status="error"
        ).inc()
        mlflow_status.set(0)
        status["errors"].append(f"Ошибка подключения: {str(e)}")

    # Добавляем статистику по методам
    status["methods_calls"] = {
        "total_predictions": predictions_by_endpoint._value.get(),
        "mlflow_methods": {
            "list_experiments": mlflow_methods_total.labels(method_name="list_experiments",
                                                            status="success")._value.get(),
            "get_latest_versions": mlflow_methods_total.labels(method_name="get_latest_versions",
                                                               status="success")._value.get()
        }
    }

    return status


# Добавляем эндпоинт для отладки метрик
@app.get("/metrics/debug")
async def metrics_debug():
    """Отладка метрик - показывает все собранные метрики"""
    from prometheus_client import REGISTRY
    metrics = {}

    for metric in REGISTRY.collect():
        if metric.name.startswith('diabetes'):
            samples = []
            for sample in metric.samples:
                samples.append({
                    'name': sample.name,
                    'labels': sample.labels,
                    'value': sample.value
                })
            metrics[metric.name] = samples

    return metrics
# from fastapi import FastAPI, HTTPException
# import numpy as np
# from mlflow import MlflowClient
#
# import random
# import os
#
# from app.schemas import PatientData, PredictionResponse
# from app.model import model_loader
#
# app = FastAPI(title="Diabetes Prediction Service")
#
#
# @app.get("/")
# async def root():
#     return {"message": "Diabetes Prediction Service"}
#
#
# @app.get("/health")
# async def health():
#     """Проверка здоровья сервиса и доступности модели"""
#     try:
#         model_loader.load_model()
#         return {"status": "healthy", "model_loaded": True}
#     except Exception as e:
#         return {"status": "unhealthy", "model_loaded": False, "error": str(e)}
#
#
# # @app.post("/api/v1/predict_test", response_model=PredictionResponse)
# # async def predict(data: PatientData):
# #     # Пока возвращаем случайное значение
# #     prediction = random.uniform(100, 300)
# #     return {"predict": round(prediction, 2)}
#
#
# @app.post("/api/v1/predict", response_model=PredictionResponse)
# async def predict(data: PatientData):
#     """
#     Предсказание прогрессии диабета на основе данных пациента
#     """
#     try:
#         # Преобразуем данные в формат для модели
#         features = [
#             data.age, data.sex, data.bmi, data.bp,
#             data.s1, data.s2, data.s3, data.s4, data.s5, data.s6
#         ]
#
#         # Получаем предсказание
#         prediction = model_loader.predict(features)
#
#         return {"predict": round(prediction, 2)}
#
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=f"Ошибка при предсказании: {str(e)}")
#
#
# @app.get("/mlflow/status")
# async def mlflow_status():
#     """Детальная проверка статуса MLflow"""
#     status = {
#         "tracking_uri": os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000"),
#         "mlflow_available": False,
#         "model_in_registry": False,
#         "local_model_exists": False,
#         "errors": []
#     }
#
#     # Проверяем локальную модель
#     from pathlib import Path
#     local_model = Path(__file__).parent.parent / "models" / "diabetes_model.joblib"
#     status["local_model_exists"] = local_model.exists()
#
#     # Проверяем MLflow
#     try:
#         import requests
#         response = requests.get(
#             f"{status['tracking_uri']}/api/2.0/mlflow/experiments/list",
#             timeout=5,
#             headers={"Host": "mlflow"}  # Добавляем заголовок Host
#         )
#
#         if response.status_code == 200:
#             status["mlflow_available"] = True
#             status["experiments"] = len(response.json().get("experiments", []))
#
#             # Проверяем наличие модели в registry
#             try:
#                 client = MlflowClient(tracking_uri=status['tracking_uri'])
#                 model_versions = client.get_latest_versions("diabetes_model")
#                 status["model_in_registry"] = len(model_versions) > 0
#                 if model_versions:
#                     status["latest_model_version"] = model_versions[0].version
#             except Exception as e:
#                 status["errors"].append(f"Ошибка при проверке registry: {str(e)}")
#         else:
#             status["errors"].append(f"HTTP {response.status_code}: {response.text}")
#
#     except Exception as e:
#         status["errors"].append(f"Ошибка подключения: {str(e)}")
#
#     return status
