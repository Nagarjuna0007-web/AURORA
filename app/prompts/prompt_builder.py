from app.prompts.system_prompt import SYSTEM_PROMPT


def build_prompt(history: str, user_message: str) -> str:
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"Conversation History:\n"
        f"{history.strip()}\n\n"
        f"User:\n"
        f"{user_message.strip()}\n\n"
        f"Aurora:"
    )