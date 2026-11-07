from app.orchestration.result_synthesizer import (
    ResultSynthesizer,
)


class MockAssistant:

    def __init__(self):
        self.messages = []

    def process(self, messages):
        self.messages.append(messages)
        return "Synthesized response"


def test_single_result_is_returned_directly():
    assistant = MockAssistant()

    synthesizer = ResultSynthesizer(
        assistant
    )

    result = synthesizer.synthesize(
        "What is Python?",
        [
            {
                "capability": "rag",
                "result": (
                    "Python is a programming language."
                ),
            }
        ],
    )

    assert result == (
        "Python is a programming language."
    )

    assert len(
        assistant.messages
    ) == 0


def test_multiple_results_are_synthesized():
    assistant = MockAssistant()

    synthesizer = ResultSynthesizer(
        assistant
    )

    result = synthesizer.synthesize(
        "What is Python and what is its latest version?",
        [
            {
                "capability": "rag",
                "result": (
                    "Python is a high-level "
                    "programming language."
                ),
            },
            {
                "capability": "web_search",
                "result": (
                    "Python 3.14.7 is the latest "
                    "stable release."
                ),
            },
        ],
    )

    assert result == "Synthesized response"

    assert len(
        assistant.messages
    ) == 1


def test_synthesizer_includes_capability_results():
    assistant = MockAssistant()

    synthesizer = ResultSynthesizer(
        assistant
    )

    synthesizer.synthesize(
        "Combine these results.",
        [
            {
                "capability": "rag",
                "result": "RAG information",
            },
            {
                "capability": "web_search",
                "result": "Web information",
            },
        ],
    )

    prompt = assistant.messages[0][0]["content"]

    assert "RAG information" in prompt
    assert "Web information" in prompt
    assert "Combine these results." in prompt


def test_web_search_is_prioritized_over_rag():
    assistant = MockAssistant()

    synthesizer = ResultSynthesizer(
        assistant
    )

    synthesizer.synthesize(
        "What is Python and what is its latest version?",
        [
            {
                "capability": "rag",
                "result": (
                    "Python 3.10.4 was previously "
                    "listed as a release."
                ),
            },
            {
                "capability": "web_search",
                "result": (
                    "Python 3.14.7 is the latest "
                    "stable release."
                ),
            },
        ],
    )

    prompt = assistant.messages[0][0]["content"]

    web_position = prompt.index(
        "CAPABILITY: web_search"
    )

    rag_position = prompt.index(
        "CAPABILITY: rag"
    )

    assert web_position < rag_position


def test_synthesizer_prompt_defines_web_priority():
    assistant = MockAssistant()

    synthesizer = ResultSynthesizer(
        assistant
    )

    synthesizer.synthesize(
        "What is the latest Python version?",
        [
            {
                "capability": "rag",
                "result": "Older information.",
            },
            {
                "capability": "web_search",
                "result": "Current information.",
            },
        ],
    )

    prompt = assistant.messages[0][0]["content"]

    assert (
        "prefer the WEB SEARCH result over RAG"
        in prompt
    )

    assert (
        "Do not use an older RAG fact to override a"
        in prompt
    )


def test_calculation_result_is_prioritized_over_rag():
    assistant = MockAssistant()

    synthesizer = ResultSynthesizer(
        assistant
    )

    synthesizer.synthesize(
        "What is 10 + 20?",
        [
            {
                "capability": "rag",
                "result": (
                    "Mathematical operations involve "
                    "numbers and operators."
                ),
            },
            {
                "capability": "calculator",
                "result": "30",
            },
        ],
    )

    prompt = assistant.messages[0][0]["content"]

    calculator_position = prompt.index(
        "CAPABILITY: calculator"
    )

    rag_position = prompt.index(
        "CAPABILITY: rag"
    )

    assert calculator_position < rag_position