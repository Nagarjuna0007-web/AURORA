from app.models.base_model import BaseModel


class DummyModel(BaseModel):

    def generate(self, prompt: str) -> str:
        return f"[Dummy Model] Response to: {prompt}"