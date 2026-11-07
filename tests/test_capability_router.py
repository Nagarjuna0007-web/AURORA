from app.routing.capability_router import CapabilityRouter

def test_capability_router():

    router = CapabilityRouter()

    test_cases = [

        # --------------------------------------------------
        # Calculator
        # --------------------------------------------------

        ("25 + 18", "calculator"),
        ("100 / 4", "calculator"),
        ("What is 25 * 4?", "calculator"),
        ("Calculate 50 - 17", "calculator"),

        # --------------------------------------------------
        # Time
        # --------------------------------------------------

        ("What time is it?", "time"),
        ("What is the current time?", "time"),
        ("Current time", "time"),
        ("Time now", "time"),
        ("time", "time"),

        # --------------------------------------------------
        # Date
        # --------------------------------------------------

        ("What is today's date?", "date"),
        ("What date is it?", "date"),
        ("What day is today?", "date"),
        ("Today's date", "date"),

        # --------------------------------------------------
        # Explicit Web Search
        # --------------------------------------------------

        ("Search for the latest AI news", "web_search"),
        ("Search online for Python news", "web_search"),
        ("Look up the latest Python version", "web_search"),
        ("Find this on the web", "web_search"),
        ("Search for recent AI developments", "web_search"),

        # --------------------------------------------------
        # Current / Latest Information
        # --------------------------------------------------

        ("What is the latest Python version?", "web_search"),
        ("What are the latest AI developments?", "web_search"),
        ("What is the current price of gold?", "web_search"),
        ("What happened today in AI?", "web_search"),
        ("What is the current weather?", "web_search"),
        ("What is the current Python version?", "web_search"),

        # --------------------------------------------------
        # RAG
        # --------------------------------------------------

        ("What is Python?", "rag"),
        ("Explain machine learning", "rag"),
        ("What is FAISS?", "rag"),
        ("What do you know about Python?", "rag"),

        # --------------------------------------------------
        # Normal
        # --------------------------------------------------

        ("Hello Aurora", "normal"),
        ("Tell me a joke", "normal"),
        ("How are you?", "normal"),

        # --------------------------------------------------
        # Boundary Cases
        # --------------------------------------------------

        ("Write a Python program", "normal"),
        ("Do you like Python?", "normal"),
        (
            "What is the difference between Python and Java?",
            "rag"
        ),
        ("Can you calculate 25 + 18?", "calculator"),
        ("Tell me about the current state of AI", "normal"),
        ("What is current Python?", "rag"),
        ("give me some time", "normal"),

        # Generic word should NOT automatically mean DateTool
        ("date", "normal"),

        # Temporal words should not override dedicated capabilities
        ("What time is it now?", "time"),
        ("What date is it today?", "date"),

        # Explicit web intent with temporal words
        ("Search for the current Python version", "web_search"),
        ("Search online for today's AI news", "web_search"),
        ("Look up the current price of gold", "web_search"),

    ]

    for query, expected_capability in test_cases:

        actual_capability = router.route(query)

        assert actual_capability == expected_capability, (
            f"Query: '{query}' | "
            f"Expected: {expected_capability} | "
            f"Got: {actual_capability}"
        )

    