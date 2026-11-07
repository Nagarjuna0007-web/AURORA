from app.engine.aurora_engine import AuroraEngine


def main():
    engine = AuroraEngine()

    try:
        engine.start()

        while True:
            user_input = input("You: ").strip()

            # Exit
            if user_input.lower() in ["exit", "quit"]:
                break

            # Empty input
            if not user_input:
                print("Aurora: Please enter a message.")
                continue

            # Help
            if user_input.lower() == "help":
                print("""
Available Commands
------------------
help     - Show available commands
history  - Show chat history
clear    - Clear chat history
stats    - Show session statistics
memory   - Show long-term memory
tools    - Show available tools
exit     - Exit Aurora
""")
                continue

            # History
            if user_input.lower() == "history":
                engine.show_history()
                continue

            # Clear History
            if user_input.lower() == "clear":
                engine.clear_history()
                continue

            # Statistics
            if user_input.lower() == "stats":
                engine.show_stats()
                continue

            # Memory
            if user_input.lower() == "memory":
                engine.show_memory()
                continue

            # Available Tools
            if user_input.lower() == "tools":
                engine.show_tools()
                continue

            # Normal chat / streaming
            print("Aurora: ", end="", flush=True)

            engine.stream_chat(user_input)

    finally:
        engine.stop()


if __name__ == "__main__":
    main()