import re
from datetime import datetime, timedelta


class WebRelevanceScorer:
    """
    Scores web search results based on
    lexical relevance, source authority,
    and temporal freshness.
    """

    def __init__(
        self,
        title_weight=2,
        snippet_weight=1,
        relevance_weight=0.5,
        authority_weight=0.3,
        freshness_weight=0.2,
    ):
        self.title_weight = title_weight
        self.snippet_weight = snippet_weight

        self.relevance_weight = relevance_weight
        self.authority_weight = authority_weight
        self.freshness_weight = freshness_weight

        self.temporal_indicators = {
            "latest",
            "current",
            "currently",
            "recent",
            "recently",
            "today",
            "tonight",
            "this week",
            "this month",
            "this year",
            "yesterday",
            "tomorrow",
            "now",
            "up to date",
            "up-to-date",
            "newest",
            "recent developments",
            "what happened",
        }

        self.stopwords = {
            "a",
            "an",
            "and",
            "are",
            "as",
            "at",
            "be",
            "by",
            "for",
            "from",
            "how",
            "is",
            "it",
            "of",
            "on",
            "or",
            "that",
            "the",
            "this",
            "to",
            "what",
            "when",
            "where",
            "who",
            "why",
            "with",
        }

    def _tokenize(self, text):
        """
        Convert text into normalized tokens.
        """

        tokens = re.findall(
            r"\b[a-zA-Z0-9]+\b",
            text.lower(),
        )

        return {
            token
            for token in tokens
            if token not in self.stopwords
        }

    def score(self, query, result):
        """
        Calculate lexical relevance between
        the query and a search result.
        """

        query_tokens = self._tokenize(query)

        if not query_tokens:
            return 0.0

        title_tokens = self._tokenize(
            result.get("title", "")
        )

        snippet_tokens = self._tokenize(
            result.get("snippet", "")
        )

        title_matches = query_tokens & title_tokens
        snippet_matches = query_tokens & snippet_tokens

        weighted_matches = (
            len(title_matches) * self.title_weight
            + len(snippet_matches) * self.snippet_weight
        )

        maximum_score = (
            len(query_tokens)
            * (
                self.title_weight
                + self.snippet_weight
            )
        )

        return weighted_matches / maximum_score

    def _is_temporal_query(self, query):
        """
        Determine whether the query requires
        current or time-sensitive information.
        """

        query = query.lower().strip()

        return any(
            indicator in query
            for indicator in self.temporal_indicators
        )

    def _parse_published_date(self, published):
        """
        Convert supported publication date formats
        into a datetime object.
        """

        if not published:
            return None

        if isinstance(published, datetime):
            return published

        published = str(published).strip().lower()

        try:
            return datetime.fromisoformat(
                published.replace("z", "+00:00")
            )
        except ValueError:
            pass

        now = datetime.now()

        relative_match = re.match(
            r"(\d+)\s+(minute|minutes|hour|hours|day|days|week|weeks)\s+ago",
            published,
        )

        if not relative_match:
            return None

        amount = int(relative_match.group(1))
        unit = relative_match.group(2)

        if "minute" in unit:
            return now - timedelta(minutes=amount)

        if "hour" in unit:
            return now - timedelta(hours=amount)

        if "day" in unit:
            return now - timedelta(days=amount)

        if "week" in unit:
            return now - timedelta(weeks=amount)

        return None

    def _freshness_score(self, result):
        """
        Calculate a normalized freshness score.

        A result published today receives a score near 1.0.
        Older results gradually lose freshness.
        """

        published = result.get("published")

        published_date = self._parse_published_date(
            published
        )

        if published_date is None:
            return 0.0

        now = datetime.now(
            published_date.tzinfo
        ) if published_date.tzinfo else datetime.now()

        age = now - published_date

        if age.total_seconds() < 0:
            return 1.0

        age_days = age.total_seconds() / 86400

        if age_days <= 1:
            return 1.0

        if age_days <= 7:
            return 0.7 - (age_days / 7) * 0.3

        if age_days <= 30:
            return 0.4 - ((age_days - 7) / 23) * 0.2

        if age_days <= 90:
            return 0.2 - ((age_days - 30) / 60) * 0.2

        return 0.0
    
    def combined_score(self, query, result):
        """
        Combine relevance, authority, and
        temporal freshness when appropriate.
        """

        relevance_score = self.score(
            query,
            result,
        )

        authority_score = result.get(
            "source_authority",
            0.0,
        )

        if self._is_temporal_query(query):
            freshness_score = self._freshness_score(
                result
            )

            return (
                relevance_score * self.relevance_weight
                + authority_score * self.authority_weight
                + freshness_score * self.freshness_weight
            )

        return (
            relevance_score * self.relevance_weight
            + authority_score * self.authority_weight
        )

    def rank(self, query, results):
        """
        Rank search results using relevance,
        authority, and temporal freshness.
        """

        if not results:
            return []

        ranked_results = []

        for result in results:

            scored_result = dict(result)

            scored_result["relevance_score"] = self.score(
                query,
                result,
            )

            scored_result["authority_score"] = result.get(
                "source_authority",
                0.0,
            )

            scored_result["freshness_score"] = (
                self._freshness_score(result)
                if self._is_temporal_query(query)
                else 0.0
            )

            scored_result["combined_score"] = (
                self.combined_score(
                    query,
                    result,
                )
            )

            ranked_results.append(scored_result)

        ranked_results.sort(
            key=lambda result: (
                result["combined_score"],
                result["freshness_score"],
            ),
            reverse=True,
        )

        return ranked_results