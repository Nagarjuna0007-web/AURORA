from app.web.web_release_validator import (
    WebReleaseValidator
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

    validator = WebReleaseValidator()

    result = validator.validate(
        results
    )

    print()
    print(
        "========== RELEASE VALIDATION =========="
    )

    for candidate in result["candidates"]:

        print(
            f"Version: {candidate['version']}"
        )

        print(
            f"Status:  {candidate['status']}"
        )

        print(
            f"Source:  {candidate['title']}"
        )

        print()

    print(
        "Stable candidates:",
        len(
            result["stable_candidates"]
        )
    )

    print(
        "Pre-release candidates:",
        len(
            result["prerelease_candidates"]
        )
    )

    print(
        "Summary:",
        result["summary"]
    )

    latest_stable = result.get(
        "latest_stable"
    )

    print()

    print(
        "Latest stable candidate:"
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

        print(
            f"Source:  "
            f"{latest_stable['title']}"
        )

    else:

        print(
            "No stable candidate found."
        )


if __name__ == "__main__":
    main()