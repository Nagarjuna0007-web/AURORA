from abc import ABC, abstractmethod


class BaseModel(ABC):
    """
    Base class for every language model used by AURORA.
    """

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """
        Generate a response for the given prompt.
        """
        pass