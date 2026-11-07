from app.rag.document_loader import DocumentLoader
from app.rag.text_chunker import TextChunker


def main():

    loader = DocumentLoader()

    text = loader.load_text(
        "data/rag_test.txt"
    )

    print("Total words:", len(text.split()))

    chunker = TextChunker(
        chunk_size=20,
        overlap=5
    )

    chunks = chunker.split(text)

    print("Document loaded successfully.")
    print(f"Total chunks: {len(chunks)}")

    print("\n========== CHUNKS ==========\n")

    for index, chunk in enumerate(chunks, start=1):

        print(f"Chunk {index}:")
        print(chunk)
        print("\n----------------------------\n")


if __name__ == "__main__":
    main()