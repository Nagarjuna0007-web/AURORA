from app.rag.document_loader import DocumentLoader


def main():

    loader = DocumentLoader()

    text = loader.load_text(
        "data/rag_test.txt"
    )

    print("Document loaded successfully.")
    print("\nDocument content:\n")
    print(text)


if __name__ == "__main__":
    main()