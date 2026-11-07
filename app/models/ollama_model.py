import time

from ollama import chat

from app.models.base_model import BaseModel
from app.prompts.system_prompt import SYSTEM_PROMPT
from app.core.config import MODEL_NAME
from app.core.logger import logger


class OllamaModel(BaseModel):

    def __init__(self):
        self.model_name = MODEL_NAME

    def generate(self, messages):
        """
        Generate a complete response.
        """

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ] + messages

        logger.debug(
            f"Sending {len(messages)} messages to the model."
        )

        start_time = time.perf_counter()

        response = chat(
            model=self.model_name,
            messages=messages
        )

        elapsed_time = time.perf_counter() - start_time

        logger.info(
            f"Ollama Generation | "
            f"Elapsed: {elapsed_time:.3f}s | "
            f"Total Duration: "
            f"{response.get('total_duration', 'N/A')} | "
            f"Load Duration: "
            f"{response.get('load_duration', 'N/A')} | "
            f"Prompt Eval Count: "
            f"{response.get('prompt_eval_count', 'N/A')} | "
            f"Prompt Eval Duration: "
            f"{response.get('prompt_eval_duration', 'N/A')} | "
            f"Eval Count: "
            f"{response.get('eval_count', 'N/A')} | "
            f"Eval Duration: "
            f"{response.get('eval_duration', 'N/A')}"
        )
        return response["message"]["content"]

    def stream(self, messages):
        """
        Stream the response token by token.
        """

        messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ] + messages

        logger.debug(
            f"Streaming {len(messages)} messages to the model."
        )

        stream = chat(
            model=self.model_name,
            messages=messages,
            stream=True
        )

        for chunk in stream:
            if "message" in chunk:
                content = chunk["message"].get("content", "")

                if content:
                    yield content

    def summarize(self, conversation):
        """
        Generate a concise summary of a conversation.
        """

        summary_prompt = [
            {
                "role": "system",
                "content": (
                    "You are an AI summarizer.\n"
                    "Summarize the conversation while preserving:\n"
                    "- Important user facts\n"
                    "- Goals\n"
                    "- Ongoing tasks\n"
                    "- Technical decisions\n"
                    "- Important context\n\n"
                    "Keep the summary concise."
                )
            },
            {
                "role": "user",
                "content": conversation
            }
        ]

        response = chat(
            model=self.model_name,
            messages=summary_prompt
        )

        return response["message"]["content"]