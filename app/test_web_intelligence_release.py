from app.web.web_intelligence import (
    WebIntelligence
)


def main():

    results = [
        {
            "title": "Python 3.14.7 released",
            "url": "https://example.com/python",
            "snippet": (
                "Python 3.14.7 is the latest stable "
                "maintenance release."
            ),
        },
        {
            "title": "Python 3.15.0rc2",
            "url": "https://example.com/rc",
            "snippet": (
                "Python 3.15.0rc2 is a release candidate."
            ),
        },
        {
            "title": "Python 3.16 development",
            "url": "https://example.com/dev",
            "snippet": (
                "Python 3.16 is currently under "
                "development."
            ),
        },
    ]

    intelligence = WebIntelligence()

    result = intelligence.analyze(
        results
    )

    validation = result[
        "release_validation"
    ]

    print()
    print(
        "========== WEB INTELLIGENCE =========="
    )

    print(
        "Evidence:",
        len(result["evidence"])
    )

    print(
        "Supporting sources:",
        len(
            result[
                "supporting_sources"
            ]
        )
    )

    print(
        "Conflicting sources:",
        len(
            result[
                "conflicting_sources"
            ]
        )
    )

    print()

    print(
        "========== RELEASE VALIDATION =========="
    )

    for candidate in validation[
        "candidates"
    ]:

        print(
            f"Version: "
            f"{candidate['version']}"
        )

        print(
            f"Status:  "
            f"{candidate['status']}"
        )

        print()

    latest_stable = validation.get(
        "latest_stable"
    )

    print(
        "Latest stable:"
    )

    if latest_stable:

        print(
            f"Version: "
            f"{latest_stable['version']}"
        )

        print(
            f"Status:  "
            f"{latest_stable['status']}"
        )

    else:

        print(
            "No stable release detected."
        )


if __name__ == "__main__":
    main()