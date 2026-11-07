from pathlib import Path


class DocumentLoader:
    """
    Loads text documents for the AURORA RAG pipeline.
    """

    def load_text(self, file_path: str) -> str:
        """
        Load a text file and return its contents.
        """

        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(
                f"Document not found: {file_path}"
            )

        if path.suffix.lower() != ".txt":
            raise ValueError(
                "DocumentLoader currently supports only .txt files."
            )

        return path.read_text(
            encoding="utf-8"
        )