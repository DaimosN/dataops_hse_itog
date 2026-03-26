import os
from pathlib import Path
import joblib
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MODEL_PATH = Path("/app/models/diabetes_model.joblib")


class ModelLoader:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def load_model(self):
        """Загрузка модели (всегда из локального файла)"""
        if self._model is not None:
            return self._model

        logger.info(f"Загрузка модели из {MODEL_PATH}")

        if not MODEL_PATH.exists():
            raise FileNotFoundError(f"Модель не найдена по пути {MODEL_PATH}")

        self._model = joblib.load(MODEL_PATH)
        logger.info("✅ Модель успешно загружена")
        return self._model

    def predict(self, features):
        """Предсказание"""
        model = self.load_model()
        prediction = model.predict([features])[0]
        return float(prediction)


model_loader = ModelLoader()
