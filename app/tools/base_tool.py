from abc import ABC, abstractmethod


class BaseTool(ABC):
    """
    Base class for every tool in AURORA.
    """

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def execute(self, *args, **kwargs):
        """
        Every tool must implement execute().
        """
        pass