from app.web.source_grounding import SourceGrounding


def test_source_grounding_creates_citations():
    grounding = SourceGrounding()

    results = [
        {
            "title": "Python Official Documentation",
            "url": "https://www.python.org/doc/",
            "snippet": "Official Python documentation.",
            "relevance_score": 0.9,
            "authority_score": 1.0,
            "freshness_score": 1.0,
            "combined_score": 0.95,
        },
        {
            "title": "Python Developer Guide",
            "url": "https://devguide.python.org/",
            "snippet": "Information for Python developers.",
            "relevance_score": 0.8,
            "authority_score": 1.0,
            "freshness_score": 0.8,
            "combined_score": 0.85,
        },
    ]

    grounded = grounding.ground(
        "What is the latest Python version?",
        results,
    )

    assert len(
        grounded["grounded_sources"]
    ) == 2

    assert grounded["grounded_sources"][0][
        "citation_id"
    ] == "[1]"

    assert grounded["grounded_sources"][1][
        "citation_id"
    ] == "[2]"


def test_source_grounding_preserves_source_information():
    grounding = SourceGrounding()

    results = [
        {
            "title": "Example Source",
            "url": "https://example.com",
            "snippet": "Example evidence.",
            "relevance_score": 0.7,
            "authority_score": 0.5,
            "freshness_score": 0.4,
            "combined_score": 0.6,
        }
    ]

    grounded = grounding.ground(
        "What is the latest Python version?",
        results,
    )
    source = grounded["grounded_sources"][0]

    assert source["title"] == "Example Source"
    assert source["url"] == "https://example.com"
    assert source["snippet"] == "Example evidence."
    assert source["relevance_score"] == 0.7
    assert source["authority_score"] == 0.5
    assert source["freshness_score"] == 0.4
    assert source["combined_score"] == 0.6


def test_source_grounding_handles_empty_results():
    grounding = SourceGrounding()

    grounded = grounding.ground(
        "What is the latest Python version?",
        [],
    )

    assert grounded["grounded_sources"] == []
    assert grounded["grounding_summary"] == ""


def test_source_grounding_limits_sources():
    grounding = SourceGrounding(
        max_sources=2
    )

    results = [
        {
            "title": "Source 1",
            "url": "https://example.com/1",
            "snippet": "Evidence 1.",
        },
        {
            "title": "Source 2",
            "url": "https://example.com/2",
            "snippet": "Evidence 2.",
        },
        {
            "title": "Source 3",
            "url": "https://example.com/3",
            "snippet": "Evidence 3.",
        },
    ]

    grounded = grounding.ground(
        "What is the latest Python version?",
        results,
    )

    assert len(
        grounded["grounded_sources"]
    ) == 2

def test_source_grounding_prioritizes_latest_official_release():
    grounding = SourceGrounding()

    results = [
        {
            "title": "Python Documentation",
            "url": "https://www.python.org/doc/versions/",
            "snippet": (
                "Python documentation and version information."
            ),
            "authority_score": 1.0,
        },
        {
            "title": "Python Release Python 3.14.7",
            "url": "https://www.python.org/downloads/latest/",
            "snippet": (
                "Python 3.14.7 is the latest stable release."
            ),
            "authority_score": 1.0,
        },
    ]

    grounded = grounding.ground(
        "What is the latest Python version?",
        results,
    )

    latest_source = grounded["grounded_sources"][1]

    assert latest_source["evidence_priority"] == "HIGH"
    assert (
        latest_source["source_type"]
        == "Official / Authoritative"
    )
def test_source_grounding_does_not_treat_old_release_as_latest():
    grounding = SourceGrounding()

    results = [
        {
            "title": "Python Documentation",
            "url": "https://www.python.org/doc/versions/",
            "snippet": (
                "Python 3.12.13, released on 3 March 2026."
            ),
            "authority_score": 1.0,
        }
    ]

    grounded = grounding.ground(
        "What is the latest Python version?",
        results,
    )

    source = grounded["grounded_sources"][0]

    assert source["source_type"] == (
        "Official / Authoritative"
    )

    assert source["supports_current_fact"] is False

    assert source["evidence_priority"] == (
        "AUTHORITATIVE"
    )