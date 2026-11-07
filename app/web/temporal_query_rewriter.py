from datetime import datetime


class TemporalQueryRewriter:
    """
    Rewrites current-information queries into
    search-engine-friendly temporal queries.
    """

    def __init__(self):
        self.today_indicators = {
            "today",
            "tonight",
            "right now",
            "happening now",
            "what happened",
        }

        self.latest_indicators = {
            "latest",
            "newest",
            "current",
            "currently",
            "recent",
            "recently",
            "up to date",
            "up-to-date",
        }

    def rewrite(self, query, current_date=None):
        """
        Rewrite a temporal query using the current date.

        Stable queries are returned unchanged.
        """

        query = query.strip()

        if not query:
            return query

        if current_date is None:
            current_date = datetime.now().strftime(
                "%Y-%m-%d"
            )

        date_object = datetime.strptime(
            current_date,
            "%Y-%m-%d",
        )

        formatted_date = (
            f"{date_object.strftime('%B')} "
            f"{date_object.day} "
            f"{date_object.year}"
        )

        normalized_query = query.lower()

        if any(
            indicator in normalized_query
            for indicator in self.today_indicators
        ):
            if "ai" in normalized_query:
                return (
                    "AI news today "
                    f"{formatted_date}"
                )

            return (
                query
                + " "
                + formatted_date
            )

        if any(
            indicator in normalized_query
            for indicator in self.latest_indicators
        ):
            cleaned_query = query.rstrip("?.!")

            prefixes = (
                "what is the ",
                "what is ",
                "what's the ",
                "what's ",
                "what are the ",
                "what are ",
            )

            lower_cleaned = cleaned_query.lower()

            for prefix in prefixes:
                if lower_cleaned.startswith(prefix):
                    cleaned_query = cleaned_query[
                        len(prefix):
                    ]
                    break

            return (
                cleaned_query
                + " "
                + formatted_date
            )

        return query