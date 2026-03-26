#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Создание различных версий промптов для модели предсказания диабета
"""

from mlflow_prompts import create_prompt_version, list_all_prompts
import json


def create_diabetes_prompts():
    """Создание всех версий промптов"""

    print("🚀 Создание версий промптов для модели предсказания диабета")
    print("=" * 60)

    # Версия 1.0 - Базовый промпт
    run_id = create_prompt_version(
        prompt_name="diabetes_prediction",
        prompt_text="""
        Предсказание прогрессии диабета на основе данных пациента.

        Входные данные:
        - age: возраст
        - sex: пол (1 - мужской, 2 - женский)
        - bmi: индекс массы тела
        - bp: среднее артериальное давление
        - s1: общий сывороточный холестерин
        - s2: липопротеины низкой плотности
        - s3: липопротеины высокой плотности
        - s4: общий холестерин / ЛПВП
        - s5: логарифм уровня триглицеридов
        - s6: уровень сахара в крови

        Модель: RandomForestRegressor с параметрами по умолчанию
        Метрики: MSE, R2
        """,
        version="1.0",
        tags={
            "author": "ML Team",
            "status": "production",
            "language": "ru",
            "domain": "healthcare"
        },
        description="Базовая версия промпта для модели случайного леса",
        model_type="random_forest",
        parameters={
            "n_estimators": 100,
            "max_depth": 10,
            "random_state": 42
        }
    )
    print(f"✅ Версия 1.0 создана (Run ID: {run_id})")

    # Версия 1.1 - Улучшенный промпт с важностью признаков
    run_id = create_prompt_version(
        prompt_name="diabetes_prediction",
        prompt_text="""
        Предсказание прогрессии диабета с учетом важности признаков.

        Топ-5 наиболее важных признаков:
        1. bmi - индекс массы тела
        2. s5 - логарифм уровня триглицеридов
        3. bp - артериальное давление
        4. s6 - уровень сахара в крови
        5. age - возраст

        Модель: RandomForestRegressor с оптимизированными параметрами
        Метрики качества:
        - R2 на тесте: ~0.44
        - MSE на тесте: ~3000
        """,
        version="1.1",
        tags={
            "author": "ML Team",
            "status": "staging",
            "language": "ru",
            "domain": "healthcare",
            "feature_importance": "included"
        },
        description="Версия с информацией о важности признаков",
        model_type="random_forest",
        parameters={
            "n_estimators": 150,
            "max_depth": 12,
            "min_samples_split": 5,
            "random_state": 42
        }
    )
    print(f"✅ Версия 1.1 создана (Run ID: {run_id})")

    # Версия 2.0 - Промпт для XGBoost модели
    run_id = create_prompt_version(
        prompt_name="diabetes_prediction",
        prompt_text="""
        Предсказание прогрессии диабета с использованием XGBoost.

        Модель: XGBoost Regressor с оптимизированными гиперпараметрами

        Параметры модели:
        - learning_rate: 0.1
        - max_depth: 6
        - n_estimators: 200
        - subsample: 0.8
        - colsample_bytree: 0.8

        Ожидаемое качество:
        - R2 на тесте: ~0.48
        - MSE на тесте: ~2800

        Особенности:
        - Автоматическая обработка пропусков
        - Регуляризация для предотвращения переобучения
        """,
        version="2.0",
        tags={
            "author": "ML Team",
            "status": "development",
            "language": "ru",
            "domain": "healthcare",
            "algorithm": "xgboost"
        },
        description="Экспериментальная версия с XGBoost",
        model_type="xgboost",
        parameters={
            "learning_rate": 0.1,
            "max_depth": 6,
            "n_estimators": 200,
            "subsample": 0.8,
            "colsample_bytree": 0.8
        }
    )
    print(f"✅ Версия 2.0 создана (Run ID: {run_id})")

    # Версия 2.1 - XGBoost с калибровкой
    run_id = create_prompt_version(
        prompt_name="diabetes_prediction",
        prompt_text="""
        Предсказание прогрессии диабета с калиброванным XGBoost.

        Модель: XGBoost Regressor с калибровкой вероятностей

        Оптимизированные параметры через GridSearchCV:
        - learning_rate: 0.05
        - max_depth: 8
        - n_estimators: 300
        - subsample: 0.7
        - colsample_bytree: 0.7
        - reg_alpha: 0.1
        - reg_lambda: 1.0

        Метрики на валидации:
        - R2: 0.52
        - RMSE: 52.8
        - MAE: 42.3

        Интервалы предсказаний:
        - 95% доверительный интервал
        - Prediction intervals включены
        """,
        version="2.1",
        tags={
            "author": "ML Team",
            "status": "testing",
            "language": "en",
            "domain": "healthcare",
            "algorithm": "xgboost",
            "calibration": "true"
        },
        description="XGBoost с калибровкой и доверительными интервалами",
        model_type="xgboost_calibrated",
        parameters={
            "learning_rate": 0.05,
            "max_depth": 8,
            "n_estimators": 300,
            "subsample": 0.7,
            "colsample_bytree": 0.7,
            "reg_alpha": 0.1,
            "reg_lambda": 1.0
        }
    )
    print(f"✅ Версия 2.1 создана (Run ID: {run_id})")

    # Версия 3.0 - LightGBM модель
    run_id = create_prompt_version(
        prompt_name="diabetes_prediction",
        prompt_text="""
        Предсказание прогрессии диабета с использованием LightGBM.

        Преимущества LightGBM:
        - Быстрое обучение
        - Низкое потребление памяти
        - Высокая точность

        Параметры модели:
        - boosting_type: 'gbdt'
        - num_leaves: 31
        - learning_rate: 0.1
        - n_estimators: 100
        - feature_fraction: 0.9
        - bagging_fraction: 0.8
        - bagging_freq: 5

        Метрики производительности:
        - Training time: ~2 seconds
        - Inference time: < 1ms per sample
        - R2 score: 0.51
        """,
        version="3.0",
        tags={
            "author": "ML Team",
            "status": "development",
            "language": "ru",
            "domain": "healthcare",
            "algorithm": "lightgbm"
        },
        description="Экспериментальная версия с LightGBM",
        model_type="lightgbm",
        parameters={
            "boosting_type": "gbdt",
            "num_leaves": 31,
            "learning_rate": 0.1,
            "n_estimators": 100,
            "feature_fraction": 0.9,
            "bagging_fraction": 0.8
        }
    )
    print(f"✅ Версия 3.0 создана (Run ID: {run_id})")

    # Версия для API с детальным описанием
    run_id = create_prompt_version(
        prompt_name="diabetes_prediction",
        prompt_text="""
        API для предсказания прогрессии диабета.

        Эндпоинт: POST /api/v1/predict

        Формат запроса (JSON):
        {
            "age": float,      # возраст
            "sex": float,      # пол (1 или 2)
            "bmi": float,      # индекс массы тела
            "bp": float,       # артериальное давление
            "s1": float,       # общий холестерин
            "s2": float,       # LDL
            "s3": float,       # HDL
            "s4": float,       # общий холестерин/HDL
            "s5": float,       # log триглицеридов
            "s6": float        # уровень сахара
        }

        Формат ответа:
        {
            "predict": float,  # предсказанное значение
            "model_version": string,  # версия модели
            "confidence": float  # уверенность предсказания (для версий 2.1+)
        }

        Модель по умолчанию: RandomForestRegressor v1.1
        """,
        version="api_v1",
        tags={
            "author": "ML Team",
            "status": "production",
            "language": "en",
            "domain": "api",
            "endpoint": "/api/v1/predict"
        },
        description="Спецификация API для предсказаний",
        model_type="api_spec",
        parameters={
            "endpoint": "/api/v1/predict",
            "method": "POST",
            "timeout": 30,
            "rate_limit": "100/minute"
        }
    )
    print(f"✅ Версия API создана (Run ID: {run_id})")


if __name__ == "__main__":
    # Создаем все версии промптов
    create_diabetes_prompts()

    # Показываем все созданные промпты
    from mlflow_prompts import list_all_prompts, compare_prompt_versions

    list_all_prompts()

    # Сравниваем версии
    compare_prompt_versions("diabetes_prediction", ["1.0", "1.1", "2.0", "2.1", "3.0"])