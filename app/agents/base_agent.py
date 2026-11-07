from abc import ABC, abstractmethod

from app.core.logger import logger


class BaseAgent(ABC):
    """
    Base class for all AURORA AI agents.
    """

    def __init__(self, name: str):
        self.name = name
        logger.info(f"Agent '{self.name}' initialized.")

    @abstractmethod
    def process(self, user_input: str) -> str:
        """
        Every agent must implement this method.
        """
        pass