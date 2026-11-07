from app.execution.capability_executor import CapabilityExecutor
from app.tools.base_tool import BaseTool
from app.tools.tool_registry import ToolRegistry


class ScalabilityTool(BaseTool):

    def __init__(self):
        super().__init__("Scalability")

    def execute(self, *args, **kwargs):
        return "Scalable tool execution successful."


class DummyRAG:

    def generate(self, message):
        return "RAG response"


class DummyAssistant:

    def respond(self, message):
        return "Assistant response"

    def stream(self, message):
        return "Assistant stream"


class DummySession:
    pass


def test_executor_uses_registry_for_new_tool():

    registry = ToolRegistry()

    scalability_tool = ScalabilityTool()

    registry.register(
        scalability_tool,
        capability="test"
    )

    executor = CapabilityExecutor(
        tool_registry=registry,
        rag=DummyRAG(),
        assistant=DummyAssistant(),
        session=DummySession(),
    )

    result = executor.execute(
        capability="test",
        message="test",
    )

    assert result == "Scalable tool execution successful."