from pyexpat.errors import messages
import re

from app.core import logger


class MemoryExtractor:
    """
    Extract structured long-term memories from user messages.
    """

    def extract(self, message):
        message = message.strip()

        memory = {}

        # -----------------------------
        # Name
        # -----------------------------
        match = re.search(
            r"my name is\s+([A-Za-z]+)$",
            message,
            re.IGNORECASE,
        )

        if not match:
            match = re.search(
                r"i am\s+([A-Za-z]+)$",
                message,
                re.IGNORECASE,
            )

        if match:
            memory["name"] = match.group(1)

        # -----------------------------
        # Location
        # -----------------------------
        match = re.search(
            r"(?:i live in|i am from)\s+(.+)",
            message,
            re.IGNORECASE,
        )

        if match:
            memory["location"] = match.group(1).strip()

        # -----------------------------
        # Project
        # -----------------------------
        match = re.search(
            r"(?:i am building|i'm building|i am working on|i'm working on)\s+(.+)",
            message,
            re.IGNORECASE,
        )

        if match:
            memory["project"] = match.group(1).strip()

        # -----------------------------
        # Profession
        # -----------------------------
        match = re.search(
            r"i am a[n]?\s+(.+)",
            message,
            re.IGNORECASE,
        )

        if match:
            memory["profession"] = match.group(1).strip()

        # -----------------------------
        # Favourite colour
        # -----------------------------
        match = re.search(
            r"my favorite color is\s+(.+)",
            message,
            re.IGNORECASE,
        )

        if match:
            memory["favorite_color"] = match.group(1).strip()

        # -----------------------------
        # Favourite food
        # -----------------------------
        match = re.search(
            r"my favorite food is\s+(.+)",
            message,
            re.IGNORECASE,
        )

        if match:
            memory["favorite_food"] = match.group(1).strip()
    
        # -----------------------------
        # Favourite programming language
        # -----------------------------
        match = re.search(
            r"my favorite programming language is\s+(.+)",
            message,
            re.IGNORECASE,
        )

        if match:
            memory["favorite_programming_language"] = match.group(1).strip()

        return memory