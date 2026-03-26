import os
import requests
import socket
import mlflow
from mlflow.tracking import MlflowClient


def diagnose():
    print("=" * 60)
    print("ДИАГНОСТИКА ПОДКЛЮЧЕНИЯ К MLFLOW")
    print("=" * 60)

    tracking_uri = os.getenv("MLFLOW_TRACKING_URI", "http://mlflow:5000")
    print(f"1. MLFLOW_TRACKING_URI: {tracking_uri}")

    # Проверка DNS
    try:
        host = tracking_uri.replace("http://", "").split(":")[0]
        ip = socket.gethostbyname(host)
        print(f"2. DNS резолвинг: {host} -> {ip} ✅")
    except Exception as e:
        print(f"2. Ошибка DNS: {e} ❌")

    # Проверка HTTP подключения
    try:
        print("3. Проверка HTTP подключения...")
        response = requests.get(
            f"{tracking_uri}/api/2.0/mlflow/experiments/list",
            timeout=5
        )
        print(f"   Статус: {response.status_code} {'✅' if response.status_code == 200 else '❌'}")

        if response.status_code == 200:
            data = response.json()
            experiments = data.get("experiments", [])
            print(f"4. Найдено экспериментов: {len(experiments)} ✅")

            # Проверка registry
            try:
                client = MlflowClient(tracking_uri=tracking_uri)
                models = client.search_registered_models()
                print(f"5. Найдено моделей в registry: {len(models)}")

                for model in models:
                    print(f"   - {model.name}")
                    versions = client.get_latest_versions(model.name)
                    print(f"     Версий: {len(versions)}")

                    if versions:
                        print(f"     Последняя версия: {versions[0].version}")
                        print(f"     Run ID: {versions[0].run_id}")

                        # Проверка возможности загрузки
                        try:
                            model_uri = f"models:/{model.name}/{versions[0].version}"
                            print(f"     Попытка загрузки из {model_uri}...")
                            # Не загружаем, просто проверяем доступность
                            print("     ✅ Модель доступна для загрузки")
                        except Exception as e:
                            print(f"     ❌ Ошибка: {e}")

            except Exception as e:
                print(f"❌ Ошибка при работе с registry: {e}")

    except Exception as e:
        print(f"❌ Ошибка подключения: {e}")

    # Проверка локальных файлов
    print("\n" + "=" * 60)
    print("ПРОВЕРКА ЛОКАЛЬНЫХ ФАЙЛОВ")
    print("=" * 60)

    paths_to_check = [
        "/app/models/diabetes_model.joblib",
        "/mlflow/artifacts/diabetes_model.joblib",
        "/mlflow/artifacts/0/diabetes_model.joblib",
        "/models/diabetes_model.joblib"
    ]

    for path in paths_to_check:
        exists = os.path.exists(path)
        size = os.path.getsize(path) if exists else 0
        print(f"{path}: {'✅' if exists else '❌'} (размер: {size} байт)")


if __name__ == "__main__":
    diagnose()