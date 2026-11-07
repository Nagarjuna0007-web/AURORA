import unittest

from app.orchestration.capability_orchestrator import CapabilityOrchestrator
from app.rag.follow_up_resolver import FollowUpResolver
from app.rag.rag_router import RAGRouter
from app.routing.capability_router import CapabilityRouter


class FollowUpResolverTests(unittest.TestCase):
    def setUp(self):
        self.r = FollowUpResolver()
        self.router = RAGRouter()

    def test_pronoun_is_resolved_to_last_topic(self):
        self.r.resolve("what is python")
        out = self.r.resolve("what else do you know about it")
        self.assertEqual(out, "what else do you know about python")
        self.assertTrue(self.router.should_use_rag(out))

    def test_the_original_follow_up_was_not_routable(self):
        self.assertFalse(self.router.should_use_rag("what else do you know about it"))

    def test_phrase_follow_ups_get_the_topic_appended(self):
        self.r.resolve("What is FAISS?")
        self.assertEqual(self.r.resolve("tell me more"), "tell me more about faiss")
        self.assertEqual(self.r.resolve("what else?"), "what else about faiss")

    def test_possessive_and_plural_pronouns(self):
        self.r.resolve("tell me about python")
        self.assertEqual(self.r.resolve("what are its uses"), "what are python's uses")
        self.assertEqual(self.r.resolve("who created them"), "who created python")

    def test_alias_is_expanded(self):
        self.r.resolve("what is ml")
        self.assertEqual(self.r.resolve("explain it"), "explain machine learning")

    def test_topic_switches_to_the_newest_topic(self):
        self.r.resolve("what is python")
        self.r.resolve("what is machine learning")
        self.assertEqual(self.r.resolve("how does it work"), "how does machine learning work")

    def test_time_questions_are_not_rewritten(self):
        self.r.resolve("what is python")
        self.assertEqual(self.r.resolve("what time is it"), "what time is it")

    def test_no_topic_yet_means_no_rewrite(self):
        self.assertEqual(self.r.resolve("what else do you know about it"), "what else do you know about it")

    def test_topic_expires_after_unrelated_turns(self):
        self.r.resolve("what is python")
        for text in ("hello", "how are you", "thanks", "nice weather", "ok"):
            self.r.resolve(text)
        self.assertEqual(self.r.resolve("tell me more"), "tell me more")

    def test_long_messages_are_left_alone(self):
        self.r.resolve("what is python")
        long_q = "i was thinking about my holiday plans last week and wondering if it will be cheaper to fly"
        self.assertEqual(self.r.resolve(long_q), long_q)

    def test_explicit_topic_in_query_is_never_rewritten(self):
        self.r.resolve("what is python")
        self.assertEqual(self.r.resolve("what is faiss and what does it do"), "what is faiss and what does it do")


class RouterTests(unittest.TestCase):
    def setUp(self):
        self.router = RAGRouter()

    def test_knowledge_questions_route_to_rag(self):
        for q in ("What is Python?", "Explain machine learning", "What is FAISS?",
                  "Tell me about artificial intelligence", "What do you know about Python?",
                  "what is a vector database", "what is rag", "tell me about python programming",
                  "who created python", "what is ml"):
            self.assertTrue(self.router.should_use_rag(q), q)

    def test_other_requests_do_not_route_to_rag(self):
        for q in ("Hello Aurora", "How are you?", "Do you like Python?", "Write a Python program",
                  "what is the capital of France", "what is a garage", "explain storage devices", ""):
            self.assertFalse(self.router.should_use_rag(q), q)


class OrchestratorIntegration(unittest.TestCase):
    def test_orchestrator_passes_the_resolved_message_and_routes_to_rag(self):
        seen = []

        class Executor:
            def execute(self, capability, message, stream=False, stream_events=False):
                seen.append((capability, message))
                return "ok"

        o = CapabilityOrchestrator(router=CapabilityRouter(), executor=Executor())
        o.orchestrate("What is Python?")
        o.orchestrate("what else do you know about it")
        self.assertEqual(seen[-1], ("rag", "what else do you know about python"))


if __name__ == "__main__":
    unittest.main()
