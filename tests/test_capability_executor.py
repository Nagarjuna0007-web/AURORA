from app.execution.capability_executor import CapabilityExecutor


class FakeTool:

    def __init__(self, name):
        self.name = name

    def execute(self, *args, **kwargs):
        if self.name == "Calculator":
            return f"CALCULATED: {args[0]}"

        if self.name == "Time":
            return "12:00:00"

        if self.name == "Date":
            return "2026-09-01"

        return "UNKNOWN"


class FakeToolRegistry:

    def __init__(self):
        self.tools = {
            "Calculator": FakeTool("Calculator"),
            "Time": FakeTool("Time"),
            "Date": FakeTool("Date"),
        }

    def get(self, name):
        return self.tools.get(name)


class FakeRAG:

    def generate(self, message):
        return f"RAG RESPONSE: {message}"


class FakeAssistant:

    def respond(self, message):
        return f"NORMAL RESPONSE: {message}"

    def stream(self, message):
        return f"STREAM RESPONSE: {message}"


class FakeSession:
    pass


def main():

    executor = CapabilityExecutor(
        tool_registry=FakeToolRegistry(),
        rag=FakeRAG(),
        assistant=FakeAssistant(),
        session=FakeSession(),
    )

    print(
        "\n========== CAPABILITY EXECUTOR TEST ==========\n"
    )

    tests = [
        ("calculator", "25 + 18"),
        ("time", "What time is it?"),
        ("date", "What is today's date?"),
        ("rag", "What is Python?"),
        ("normal", "Hello Aurora"),
    ]

    for capability, message in tests:

        result = executor.execute(
            capability,
            message,
        )

        print(f"Capability : {capability}")
        print(f"Message    : {message}")
        print(f"Result     : {result}")
        print()


if __name__ == "__main__":
    main()