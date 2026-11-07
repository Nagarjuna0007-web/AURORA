from app.core.logger import logger


class RAGGenerator:
    """
    Generates answers using relevant retrieved documents
    as context.
    """

    def __init__(self, model):
        self.model = model

    def generate(self, query, retrieved_documents):
        """
        Generate a grounded answer using already-filtered
        retrieved documents.
        """

        if not retrieved_documents:
            return (
                "I could not find this information in the "
                "knowledge base."
            )

        context = "\n\n".join(
            f"[Source {index + 1}]\n{document['document']}"
            for index, document in enumerate(
                retrieved_documents
            )
        )

        messages = [
            {
                "role": "system",
                "content": (
                "You are AURORA's knowledge-base assistant.\n\n"

                "You MUST answer using ONLY the information contained "
                "in the Retrieved Context.\n\n"

                "GROUNDING RULES:\n"
                "1. Do not use your pretrained knowledge.\n"
                "2. Do not add facts, examples, definitions, or explanations "
                "that are not explicitly present in the Retrieved Context.\n"
                "3. Do not expand the answer using general knowledge.\n"
                "4. Do not infer information from the context.\n"
                "5. If the context does not directly answer the question, "
                "respond exactly with:\n"
                "\"I could not find this information in the knowledge base.\"\n"
                "6. Keep the answer concise.\n"
                "7. Use only statements that can be directly supported "
                "by the Retrieved Context.\n"
                "8. Answer the question directly and concisely.\n"
                "9. Do not discuss irrelevant information from the context.\n"
                "10. Do not mention the retrieval process or explain which "
                "parts of the context were relevant or irrelevant.\n\n"

                "IMPORTANT:\n"
                "The Retrieved Context is your ONLY source of truth."
            )
            },
            {
                "role": "user",
                "content": (
                    f"Retrieved Context:\n\n"
                    f"{context}\n\n"
                    f"Question:\n{query}"
                ),
            },
        ]

        logger.info(
            f"Generating grounded RAG answer using "
            f"{len(retrieved_documents)} relevant documents."
        )

        return self.model.generate(messages)