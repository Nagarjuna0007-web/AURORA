from app.web.web_relevance_scorer import WebRelevanceScorer


def test_authoritative_source_can_outscore_secondary_source():
    scorer = WebRelevanceScorer()

    results = [
        {
            "title": "Python 3.14.7",
            "snippet": "Latest stable Python release",
            "source_authority": 1.0,
        },
        {
            "title": "Latest Python Version",
            "snippet": "Python 3.14 is the latest version",
            "source_authority": 0.0,
        },
    ]

    ranked = scorer.rank(
        "What is the latest Python version?",
        results,
    )

    assert ranked[0]["source_authority"] == 1.0


def test_fresh_result_can_outscore_old_result_for_current_query():
    scorer = WebRelevanceScorer()

    results = [
        {
            "title": "AI News",
            "snippet": "AI developments",
            "source_authority": 0.0,
            "published": "2026-08-21",
        },
        {
            "title": "AI News",
            "snippet": "AI developments",
            "source_authority": 0.0,
            "published": "2026-09-09",
        },
    ]

    ranked = scorer.rank(
        "What happened today in AI?",
        results,
    )

    assert ranked[0]["published"] == "2026-09-09"