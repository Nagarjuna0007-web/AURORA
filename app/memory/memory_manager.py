class MemoryManager:
    """
    Stores important long-term user information.
    """

    def __init__(self):
        self.memory = {}

    def remember(self, key, value):
        """
        Save or update a memory.
        """
        self.memory[key] = value

    def recall(self, key):
        """
        Retrieve a stored memory.
        """
        return self.memory.get(key)

    def get_all(self):
        """
        Return all stored memories.
        """
        return self.memory

    def clear(self):
        """
        Remove all stored memories.
        """
        self.memory.clear()