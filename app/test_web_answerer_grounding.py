from app.web.web_answerer import WebAnswerer


class MockAssistant:
    def __init__(self):
        self.prompt = None

    def stream(self, prompt):
        self.prompt = prompt
        yield "Test answer."


def test_web_answerer_includes_citation_ids():
    assistant = MockAssistant()
    answerer = WebAnswerer(assistant)

    results = [
        {
            "title": "Python Official Documentation",
            "url": "https://www.python.org/doc/",
            "snippet": "Python is a programming language.",
        },
        {
            "title": "Python Developer Guide",
            "url": "https://devguide.python.org/",
            "snippet": "Python development information.",
        },
    ]

    grounding = {
        "grounded_sources": [
            {
                "citation_id": "[1]",
                "title": "Python Official Documentation",
                "url": "https://www.python.org/doc/",
                "snippet": "Python is a programming language.",
            },
            {
                "citation_id": "[2]",
                "title": "Python Developer Guide",
                "url": "https://devguide.python.org/",
                "snippet": "Python development information.",
            },
        ],
        "grounding_summary": (
            "2 source(s) are available for citation."
        ),
    }

    answerer.answer(
        "What is Python?",
        results,
        grounding=grounding,
    )

    # Evidence is labelled with the citation IDs, without double brackets.
    assert "[1] Title: Python Official Documentation" in assistant.prompt
    assert "[2] Title: Python Developer Guide" in assistant.prompt
    assert "[[1]]" not in assistant.prompt
    assert "Use only citation IDs provided in the evidence" in assistant.prompt


def test_web_answerer_without_grounding_still_works():
    assistant = MockAssistant()
    answerer = WebAnswerer(assistant)

    results = [
        {
            "title": "Example Source",
            "url": "https://example.com",
            "snippet": "Example evidence.",
        }
    ]

    answerer.answer(
        "What is this?",
        results,
    )

    assert "Example Source" in assistant.prompt
    assert "Example evidence." in assistant.prompt


def test_web_answerer_preserves_sources():
    assistant = MockAssistant()
    answerer = WebAnswerer(assistant)

    results = [
        {
            "title": "Source A",
            "url": "https://example.com/a",
            "snippet": "Evidence A.",
        },
        {
            "title": "Source B",
            "url": "https://example.com/b",
            "snippet": "Evidence B.",
        },
    ]

    response = answerer.answer(
        "Test question",
        results,
    )

    assert "Sources:" in response
    assert "1. Source A" in response
    assert "2. Source B" in response