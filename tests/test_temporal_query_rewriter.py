from app.web.temporal_query_rewriter import TemporalQueryRewriter


def test_rewrites_today_ai_query():
    rewriter = TemporalQueryRewriter()

    rewritten = rewriter.rewrite(
        "What happened today in AI?",
        current_date="2026-09-09",
    )

    assert rewritten == "AI news today September 9 2026"


def test_rewrites_latest_query():
    rewriter = TemporalQueryRewriter()

    rewritten = rewriter.rewrite(
        "What is the latest Python version?",
        current_date="2026-09-09",
    )

    assert rewritten == "latest Python version September 9 2026"


def test_preserves_stable_query():
    rewriter = TemporalQueryRewriter()

    rewritten = rewriter.rewrite(
        "What is Python?",
        current_date="2026-09-09",
    )

    assert rewritten == "What is Python?"