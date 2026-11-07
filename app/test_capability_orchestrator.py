from app.routing.capability_router import CapabilityRouter
from app.orchestration.capability_orchestrator import (
    CapabilityOrchestrator,
)


class MockExecutor:

    def __init__(self):
        self.executed = []

    def execute(
        self,
        capability,
        message,
        stream=False,
        stream_events=False,
    ):
        self.executed.append(
            capability
        )

        return (
            f"Mock result from {capability}"
        )


def test_orchestrator_executes_single_capability():

    router = CapabilityRouter()

    executor = MockExecutor()

    orchestrator = CapabilityOrchestrator(
        router=router,
        executor=executor,
    )

    result = orchestrator.orchestrate(
        "What is Python?"
    )

    assert "rag" in result["capabilities"]

    assert "rag" in executor.executed


def test_orchestrator_detects_web_capability():

    router = CapabilityRouter()

    executor = MockExecutor()

    orchestrator = CapabilityOrchestrator(
        router=router,
        executor=executor,
    )

    result = orchestrator.orchestrate(
        "What is the latest Python version?"
    )

    assert "web_search" in result["capabilities"]

    assert "web_search" in executor.executed


def test_orchestrator_avoids_duplicate_capabilities():

    router = CapabilityRouter()

    executor = MockExecutor()

    orchestrator = CapabilityOrchestrator(
        router=router,
        executor=executor,
    )

    result = orchestrator.orchestrate(
        "What is the latest Python version?"
    )

    assert (
        len(result["capabilities"])
        == len(
            set(result["capabilities"])
        )
    )


def test_orchestrator_prioritizes_web_for_current_information():

    router = CapabilityRouter()

    executor = MockExecutor()

    orchestrator = CapabilityOrchestrator(
        router=router,
        executor=executor,
    )

    result = orchestrator.orchestrate(
        "What is the latest Python version?"
    )

    assert result["capabilities"] == [
        "web_search"
    ]

    assert executor.executed == [
        "web_search"
    ]


def test_orchestrator_keeps_rag_for_static_knowledge():

    router = CapabilityRouter()

    executor = MockExecutor()

    orchestrator = CapabilityOrchestrator(
        router=router,
        executor=executor,
    )

    result = orchestrator.orchestrate(
        "What is Python?"
    )

    assert result["capabilities"] == [
        "rag"
    ]

    assert executor.executed == [
        "rag"
    ]
    
def test_orchestrator_detects_rag_and_web_for_multi_intent_query():

    router = CapabilityRouter()

    executor = MockExecutor()

    orchestrator = CapabilityOrchestrator(
        router=router,
        executor=executor,
    )

    result = orchestrator.orchestrate(
        "What is Python and what is its latest version?"
    )

    assert result["capabilities"] == [
        "rag",
        "web_search",
    ]

    assert executor.executed == [
        "rag",
        "web_search",
    ]
def test_orchestrator_detects_calculation_capability():
    router = CapabilityRouter()

    executor = MockExecutor()

    orchestrator = CapabilityOrchestrator(
        router=router,
        executor=executor,
    )

    result = orchestrator.orchestrate(
        "What is 25 + 75?"
    )

    assert result["capabilities"] == [
        "calculator"
    ]

    assert executor.executed == [
        "calculator"
    ]