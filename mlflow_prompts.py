"""
Управление промптами в MLflow Prompt Storage
Создание, версионирование и управление промптами
"""

import mlflow
from mlflow import MlflowClient
import pandas as pd
from datetime import datetime
import json
import os

# Настройка подключения к MLflow
MLFLOW_TRACKING_URI = "http://localhost:5000"
mlflow.set_tracking_uri(MLFLOW_TRACKING_URI)
client = MlflowClient(tracking_uri=MLFLOW_TRACKING_URI)

# Создаем эксперимент для промптов
PROMPT_EXPERIMENT_NAME = "diabetes_prediction_prompts"
experiment = mlflow.set_experiment(PROMPT_EXPERIMENT_NAME)

print(f"✅ Подключен к MLflow: {MLFLOW_TRACKING_URI}")
print(f"📊 Эксперимент: {PROMPT_EXPERIMENT_NAME} (ID: {experiment.experiment_id})")


def create_prompt_version(
        prompt_name: str,
        prompt_text: str,
        version: str,
        tags: dict = None,
        description: str = "",
        model_type: str = "random_forest",
        parameters: dict = None
):
    """
    Создание новой версии промпта в MLflow

    Args:
        prompt_name: Название промпта
        prompt_text: Текст промпта
        version: Версия промпта
        tags: Теги для промпта
        description: Описание промпта
        model_type: Тип модели
        parameters: Параметры модели
    """

    with mlflow.start_run(run_name=f"{prompt_name}_v{version}"):
        # Логируем теги
        if tags:
            for key, value in tags.items():
                mlflow.set_tag(key, value)

        # Основные теги
        mlflow.set_tag("prompt_name", prompt_name)
        mlflow.set_tag("prompt_version", version)
        mlflow.set_tag("model_type", model_type)
        mlflow.set_tag("created_at", datetime.now().isoformat())
        mlflow.set_tag("description", description)

        # Логируем параметры
        mlflow.log_param("prompt_name", prompt_name)
        mlflow.log_param("prompt_version", version)
        mlflow.log_param("model_type", model_type)

        if parameters:
            for key, value in parameters.items():
                mlflow.log_param(f"param_{key}", value)

        # Логируем сам промпт как артефакт
        prompt_info = {
            "name": prompt_name,
            "version": version,
            "text": prompt_text,
            "description": description,
            "model_type": model_type,
            "parameters": parameters,
            "created_at": datetime.now().isoformat(),
            "tags": tags
        }

        # Сохраняем промпт в файл
        prompt_file = f"prompt_{prompt_name}_v{version}.json"
        with open(prompt_file, 'w', encoding='utf-8') as f:
            json.dump(prompt_info, f, ensure_ascii=False, indent=2)

        # Логируем файл как артефакт
        mlflow.log_artifact(prompt_file)

        # Удаляем временный файл
        os.remove(prompt_file)

        # Также логируем текст промпта отдельно
        mlflow.log_text(prompt_text, f"prompt_v{version}.txt")

        # Регистрируем промпт в Model Registry
        try:
            mlflow.register_model(
                model_uri=f"runs:/{mlflow.active_run().info.run_id}/prompt",
                name=f"prompt_{prompt_name}"
            )
            print(f"  ✅ Промпт зарегистрирован в Model Registry")
        except Exception as e:
            print(f"  ⚠️ Не удалось зарегистрировать в Model Registry: {e}")

        return mlflow.active_run().info.run_id


def list_all_prompts():
    """Получение списка всех промптов"""
    print("\n📋 Все версии промптов:")
    print("-" * 80)

    runs = mlflow.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["start_time DESC"]
    )

    if runs.empty:
        print("❌ Промпты не найдены")
        return runs

    for idx, run in runs.iterrows():
        print(f"\n🆔 Run ID: {run.run_id}")
        print(f"  📝 Название: {run.get('tags.prompt_name', 'N/A')}")
        print(f"  🔖 Версия: {run.get('tags.prompt_version', 'N/A')}")
        print(f"  🤖 Модель: {run.get('tags.model_type', 'N/A')}")
        print(f"  📅 Создан: {run.get('tags.created_at', 'N/A')}")
        print(f"  📊 Статус: {run.status}")

    return runs


def get_prompt_by_version(prompt_name: str, version: str = "latest"):
    """
    Получение промпта по имени и версии

    Args:
        prompt_name: Название промпта
        version: Версия ("latest" или конкретный номер)
    """
    runs = mlflow.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string=f"tags.prompt_name = '{prompt_name}'",
        order_by=["start_time DESC"]
    )

    if runs.empty:
        print(f"❌ Промпт '{prompt_name}' не найден")
        return None

    if version == "latest":
        run_id = runs.iloc[0].run_id
    else:
        version_runs = runs[runs['tags.prompt_version'] == version]
        if version_runs.empty:
            print(f"❌ Версия {version} не найдена")
            return None
        run_id = version_runs.iloc[0].run_id

    # Получаем артефакты
    artifacts = mlflow.artifacts.list_artifacts(run_id)

    # Ищем JSON файл с промптом
    prompt_data = None
    for artifact in artifacts:
        if artifact.path.endswith('.json'):
            local_path = mlflow.artifacts.download_artifacts(
                run_id=run_id,
                artifact_path=artifact.path
            )
            with open(local_path, 'r', encoding='utf-8') as f:
                prompt_data = json.load(f)
            os.remove(local_path)
            break

    return prompt_data


def compare_prompt_versions(prompt_name: str, versions: list = None):
    """
    Сравнение версий промптов

    Args:
        prompt_name: Название промпта
        versions: Список версий для сравнения
    """
    runs = mlflow.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string=f"tags.prompt_name = '{prompt_name}'",
        order_by=["start_time DESC"]
    )

    if runs.empty:
        print(f"❌ Промпт '{prompt_name}' не найден")
        return

    if versions:
        runs = runs[runs['tags.prompt_version'].isin(versions)]

    print(f"\n📊 Сравнение версий промпта '{prompt_name}':")
    print("-" * 100)

    comparison_data = []
    for idx, run in runs.iterrows():
        prompt_data = get_prompt_by_version(prompt_name, run['tags.prompt_version'])
        comparison_data.append({
            "Версия": run['tags.prompt_version'],
            "Модель": run['tags.model_type'],
            "Дата": run['tags.created_at'][:10] if run['tags.created_at'] != 'None' else 'N/A',
            "Параметры": prompt_data.get('parameters', {}) if prompt_data else {}
        })

    df = pd.DataFrame(comparison_data)
    print(df.to_string(index=False))

    return df


def delete_prompt_version(prompt_name: str, version: str):
    """Удаление конкретной версии промпта"""
    runs = mlflow.search_runs(
        experiment_ids=[experiment.experiment_id],
        filter_string=f"tags.prompt_name = '{prompt_name}' and tags.prompt_version = '{version}'"
    )

    if runs.empty:
        print(f"❌ Версия {version} промпта '{prompt_name}' не найдена")
        return False

    run_id = runs.iloc[0].run_id
    client.delete_run(run_id)
    print(f"✅ Версия {version} промпта '{prompt_name}' удалена")
    return True


def export_prompts_to_file(filename="prompts_export.json"):
    """Экспорт всех промптов в JSON файл"""
    runs = mlflow.search_runs(
        experiment_ids=[experiment.experiment_id],
        order_by=["start_time DESC"]
    )

    all_prompts = []
    for idx, run in runs.iterrows():
        prompt_data = get_prompt_by_version(
            run['tags.prompt_name'],
            run['tags.prompt_version']
        )
        if prompt_data:
            all_prompts.append(prompt_data)

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(all_prompts, f, ensure_ascii=False, indent=2)

    print(f"✅ Экспортировано {len(all_prompts)} промптов в {filename}")
    return filename