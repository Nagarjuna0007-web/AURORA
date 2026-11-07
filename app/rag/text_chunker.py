from typing import List


class TextChunker:
    """
    Splits documents into overlapping word-based chunks
    for embedding and retrieval.
    """

    def __init__(
        self,
        chunk_size: int = 40,
        overlap: int = 10
    ):
        if chunk_size <= 0:
            raise ValueError("chunk_size must be greater than 0.")

        if overlap < 0:
            raise ValueError("overlap cannot be negative.")

        if overlap >= chunk_size:
            raise ValueError(
                "overlap must be smaller than chunk_size."
            )

        self.chunk_size = chunk_size
        self.overlap = overlap

    def split(self, text: str) -> List[str]:
        """
        Split text into overlapping word-based chunks.
        """

        text = text.strip()

        if not text:
            return []

        words = text.split()

        chunks = []

        start = 0

        while start < len(words):

            end = start + self.chunk_size

            chunk = " ".join(words[start:end])

            if chunk:
                chunks.append(chunk)

            start += self.chunk_size - self.overlap

        return chunks