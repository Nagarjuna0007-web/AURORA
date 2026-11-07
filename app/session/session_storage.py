import json
from pathlib import Path

from app.core.logger import logger


class SessionStorage:

    def __init__(self):
        self.file_path = (
            Path(__file__).resolve().parent.parent.parent
            / "data"
            / "history.json"
        )

    def load_history(self):

        try:
            if not self.file_path.exists():
                return []

            with open(self.file_path, "r", encoding="utf-8") as file:
                return json.load(file)

        except Exception:
            logger.exception("Failed to load chat history.")
            return []

    def save_history(self, history):

        try:
            with open(self.file_path, "w", encoding="utf-8") as file:
                json.dump(history, file, indent=4)

        except Exception:
            logger.exception("Failed to save chat history.")