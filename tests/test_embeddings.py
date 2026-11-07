from app.rag.huggingface_embeddings import HuggingFaceEmbeddingModel


def main():
    model = HuggingFaceEmbeddingModel(
        "sentence-transformers/all-MiniLM-L6-v2"
    )

    text = "Python is a programming language."

    vector = model.embed(text)

    print("Embedding generated successfully.")
    print("Vector dimensions:", len(vector))
    print("First 5 values:", vector[:5])


if __name__ == "__main__":
    main()