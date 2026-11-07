from ddgs import DDGS

from app.tools.base_tool import BaseTool
from app.web.web_result_processor import WebResultProcessor
from app.web.web_relevance_scorer import WebRelevanceScorer
from app.web.temporal_query_rewriter import TemporalQueryRewriter


class WebSearchTool(BaseTool):
    """
    Performs a web search and returns relevant
    processed search results.
    """

    def __init__(self):
        super().__init__("Web Search")

        self.processor = WebResultProcessor()
        self.scorer = WebRelevanceScorer()
        self.temporal_rewriter = TemporalQueryRewriter()

    def execute(self, query):
        query = query.strip()

        if not query:
            raise ValueError("Search query cannot be empty.")

        search_query = self.temporal_rewriter.rewrite(
            query
        )

        results = DDGS().text(
            search_query,
            max_results=5,
        )

        processed_results = self.processor.process(
            results
        )

        return self.scorer.rank(
            search_query,
            processed_results,
        )