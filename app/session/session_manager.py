from datetime import datetime

from app.session.session_storage import SessionStorage

from app.core.config import CONTEXT_WINDOW

from app.core.logger import logger

from app.memory.summary_manager import SummaryManager

from app.memory.memory_manager import MemoryManager

from app.prompts.system_prompt import SYSTEM_PROMPT

class SessionManager:

    def __init__(self):
        self.storage = SessionStorage()
        self.summary_manager = SummaryManager()
        self.memory_manager = MemoryManager()
        self.history = self.storage.load_history()
        self.start_time = datetime.now()

    def add_message(self, role, message):
        self.history.append({
            "role": role,
            "message": message
        })

        self.storage.save_history(self.history)


    def get_history(self):
        return self.history

    def clear_history(self):
        self.history.clear()
        self.storage.save_history(self.history)

    def get_messages_for_model(self, user_message=None):
        messages = []

        # AURORA identity and behavior
        messages.append({
            "role": "system",
            "content": SYSTEM_PROMPT
        })

        # Conversation summary
        summary = self.summary_manager.get_summary()

        if summary:
            messages.append({
                "role": "system",
                "content": f"Conversation Summary:\n{summary}"
            })

        # Long-term memory
        memories = self.memory_manager.get_all()

        if memories:
            relevant_memories = memories

            if user_message:
                user_words = set(
                    user_message.lower().split()
                )

                relevant_memories = {}

                for key, value in memories.items():
                    key_words = set(
                        key.lower().replace("_", " ").split()
                    )

                    value_words = set(
                        str(value).lower().split()
                    )

                    if (
                        user_words & key_words
                        or user_words & value_words
                    ):
                        relevant_memories[key] = value

            if relevant_memories:
                memory_text = "\n".join(
                    f"- {key}: {value}"
                    for key, value in relevant_memories.items()
                )

                messages.append({
                    "role": "system",
                    "content": f"Relevant Long-Term Memory:\n{memory_text}"
                })

                logger.debug(
                    f"Using {len(relevant_memories)} relevant memories "
                    f"out of {len(memories)} stored memories."
                )

            else:
                logger.debug(
                    f"No relevant long-term memories found for: "
                    f"{user_message}"
                )

        # Recent conversation
        recent_history = self.history[-CONTEXT_WINDOW:]

        logger.debug(
            f"Sending {len(recent_history)} recent messages "
            f"with summary to the model."
        )

        for item in recent_history:
            role = "assistant" if item["role"] == "Aurora" else "user"

            messages.append({
                "role": role,
                "content": item["message"]
            })

        return messages

    def total_messages(self):
        return len(self.history)
    
    def get_summary(self):
        return self.summary_manager.get_summary()

    def update_summary(self, summary):
        self.summary_manager.update_summary(summary)

    def clear_summary(self):
        self.summary_manager.clear() 

    def remember(self, key, value):
        """
        Store a long-term memory.
        """
        self.memory_manager.remember(key, value)


    def recall(self, key):
        """
        Retrieve a stored memory.
        """
        return self.memory_manager.recall(key)


    def get_memories(self):
        """
        Return all long-term memories.
        """
        return self.memory_manager.get_all()


    def clear_memory(self):
        """
        Clear all stored memories.
        """
        self.memory_manager.clear()    

    def should_summarize(self):
        """
        Returns True when the conversation exceeds
        twice the configured context window.
        """
        return len(self.history) > (CONTEXT_WINDOW * 2)
            
    