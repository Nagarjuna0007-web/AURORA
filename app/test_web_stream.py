from app.engine.aurora_engine import AuroraEngine


def main():

    engine = AuroraEngine()

    print("\n========== WEB STREAM TEST ==========\n")

    response_chunks = []

    for chunk in engine.web_stream_chat(
        "Explain what Python is in a simple way."
    ):

        print(
            chunk,
            end="",
            flush=True,
        )

        response_chunks.append(chunk)

    print(
        "\n\n========== STREAM COMPLETE ==========\n"
    )

    print(
        f"Collected characters: "
        f"{len(''.join(response_chunks))}"
    )


if __name__ == "__main__":
    main()