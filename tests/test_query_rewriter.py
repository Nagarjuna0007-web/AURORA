from app.rag.query_rewriter import QueryRewriter


def main():

    rewriter = QueryRewriter()

    queries = [
        "What is ML?",
        "Explain AI",
        "Tell me about NLP",
        "What is Python?",
    ]

    print("\n========== QUERY REWRITER TEST ==========\n")

    for query in queries:

        rewritten = rewriter.rewrite(query)

        print(f"Original : {query}")
        print(f"Rewritten: {rewritten}")
        print("\n----------------------------")


if __name__ == "__main__":
    main()