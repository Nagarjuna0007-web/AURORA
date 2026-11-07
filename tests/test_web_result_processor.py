from app.web.web_result_processor import WebResultProcessor


def test_processor_preserves_relative_publication_time():
    processor = WebResultProcessor()

    results = [
        {
            "title": "AI News Today",
            "href": "https://example.com/ai-news",
            "body": "6 hours ago - Latest AI developments.",
        }
    ]

    processed = processor.process(results)

    assert len(processed) == 1
    assert processed[0]["published"] == "6 hours ago"


def test_processor_preserves_explicit_publication_date():
    processor = WebResultProcessor()

    results = [
        {
            "title": "AI Research",
            "href": "https://example.com/ai-research",
            "body": "September 9, 2026 - New AI research.",
        }
    ]

    processed = processor.process(results)

    assert len(processed) == 1
    assert processed[0]["published"] == "September 9, 2026"
    
def test_processor_extracts_date_from_middle_of_snippet():
    processor = WebResultProcessor()

    results = [
        {
            "title": "Artificial intelligence - IBM Newsroom",
            "href": "https://newsroom.ibm.com/latest-news-artificial-intelligence",
            "body": (
                "Advance to Finals for 2026. "
                "Sep 9, 2026 Artificial intelligence "
                "New IBM Study Finds AI Adoption Is Outpacing K-12 Readiness"
            ),
        }
    ]

    processed = processor.process(results)

    assert len(processed) == 1
    assert processed[0]["published"] == "Sep 9, 2026"