from app.web.web_intelligence import WebIntelligence


def test_web_intelligence_extracts_evidence():
    intelligence = WebIntelligence()

    results = [
        {
            "title": "Python Official Release",
            "url": "https://python.org/release",
            "snippet": (
                "Python 3.14 is the latest stable release "
                "of the Python programming language."
            ),
            "source_authority": 1.0,
            "relevance_score": 0.9,
            "freshness_score": 1.0,
            "combined_score": 0.95,
        },
        {
            "title": "Python Documentation",
            "url": "https://docs.python.org",
            "snippet": (
                "Python 3.14 is the latest stable version "
                "available for developers."
            ),
            "source_authority": 1.0,
            "relevance_score": 0.8,
            "freshness_score": 1.0,
            "combined_score": 0.9,
        },
        {
            "title": "Python Community",
            "url": "https://example.com/python",
            "snippet": (
                "Python provides extensive libraries and "
                "tools for application development."
            ),
            "source_authority": 0.0,
            "relevance_score": 0.6,
            "freshness_score": 0.5,
            "combined_score": 0.55,
        },
    ]

    analysis = intelligence.analyze(results)

    assert len(analysis["evidence"]) == 3
    assert analysis["evidence"][0]["title"] == (
        "Python Official Release"
    )


def test_web_intelligence_detects_supporting_sources():
    intelligence = WebIntelligence()

    results = [
        {
            "title": "Source A",
            "url": "https://example.com/a",
            "snippet": (
                "Python 3.14 latest stable release "
                "available today."
            ),
        },
        {
            "title": "Source B",
            "url": "https://example.com/b",
            "snippet": (
                "Python 3.14 latest stable version "
                "available today."
            ),
        },
    ]

    analysis = intelligence.analyze(results)

    assert len(
        analysis["supporting_sources"]
    ) >= 1


def test_web_intelligence_handles_empty_results():
    intelligence = WebIntelligence()

    analysis = intelligence.analyze([])

    assert analysis["evidence"] == []
    assert analysis["supporting_sources"] == []
    assert analysis["conflicting_sources"] == []
    assert analysis["summary"] == ""