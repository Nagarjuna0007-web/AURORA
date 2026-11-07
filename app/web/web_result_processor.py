import re

from urllib.parse import urlparse


class WebResultProcessor:
    """
    Cleans, filters, deduplicates, and prepares
    raw web search results.
    """

    def __init__(self, max_results=5):
        self.max_results = max_results

        # Trusted domains that commonly provide
        # authoritative information.
        self.authoritative_domains = {
            # Python
            "python.org",
            "docs.python.org",
            "devguide.python.org",

            # Microsoft
            "microsoft.com",
            "learn.microsoft.com",

            # GitHub
            "github.com",
            "docs.github.com",

            # Google
            "google.com",
            "developers.google.com",

            # OpenAI
            "openai.com",
            "platform.openai.com",

            # Meta
            "meta.com",
            "ai.meta.com",

            # AWS
            "amazon.com",
            "aws.amazon.com",

            # Government
            "gov",
            "gov.in",
        }

    def process(self, results):
        """
        Convert raw web search results into a clean,
        deduplicated structure.
        """

        if not results:
            return []

        processed_results = []
        seen_urls = set()

        for result in results:

            title = result.get(
                "title",
                ""
            ).strip()

            url = result.get(
                "href",
                ""
            ).strip()

            snippet = result.get(
                "body",
                ""
            ).strip()

            if not title or not url:
                continue

            normalized_url = url.rstrip("/").lower()

            if normalized_url in seen_urls:
                continue

            seen_urls.add(normalized_url)

            published = self._extract_publication_time(
                snippet
            )

            processed_results.append(
                {
                    "title": title,
                    "url": url,
                    "snippet": snippet,
                    "published": published,
                    "source_authority": self._get_source_authority(
                        url
                    ),
                }
            )

        # Keep the strongest results available to the
        # relevance scorer. Do not use snippet length
        # as a proxy for quality.
        processed_results.sort(
            key=lambda result: result["source_authority"],
            reverse=True,
        )

        return processed_results[:self.max_results]

    def _extract_publication_time(self, snippet):
        """
        Extract publication timing information from
        a search-result snippet.
        """

        if not snippet:
            return None

        # Relative timestamps returned by DDGS,
        # such as:
        # "6 hours ago"
        # "18 hours ago"
        # "2 days ago"
        # "1 week ago"
        relative_match = re.search(
            r"\b(\d+\s+"
            r"(?:minute|minutes|hour|hours|day|days|week|weeks)"
            r"\s+ago)\b",
            snippet,
            re.IGNORECASE,
        )

        if relative_match:
            return relative_match.group(1)

        # Explicit dates such as:
        # "September 9, 2026"
        # "Sep 9, 2026"
        date_match = re.search(
            r"\b("
            r"(?:January|February|March|April|May|June|July|"
            r"August|September|October|November|December|"
            r"Jan|Feb|Mar|Apr|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)"
            r"\s+\d{1,2},\s+\d{4}"
            r")\b",
            snippet,
            re.IGNORECASE,
        )

        if date_match:
            return date_match.group(1)

        return None

    def _get_source_authority(self, url):
        """
        Assign an authority score based on the result's
        domain.
        """

        try:
            hostname = urlparse(url).hostname

            if not hostname:
                return 0

            hostname = hostname.lower()

            # Remove www. for consistent comparison.
            if hostname.startswith("www."):
                hostname = hostname[4:]

            # Exact authoritative domain.
            if hostname in self.authoritative_domains:
                return 1.0

            # Government domains such as *.gov and *.gov.in.
            if hostname.endswith(".gov"):
                return 1.0

            if hostname.endswith(".gov.in"):
                return 1.0

            # Subdomains of known authoritative domains.
            for domain in self.authoritative_domains:
                if domain in {
                    "gov",
                    "gov.in",
                }:
                    continue

                if hostname.endswith("." + domain):
                    return 1.0

        except Exception:
            return 0.0

        return 0.0