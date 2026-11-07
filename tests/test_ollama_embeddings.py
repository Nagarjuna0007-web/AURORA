import unittest

from app.rag.embedding_factory import build_embedding_model
from app.rag.ollama_embeddings import BATCH_SIZE, OllamaEmbeddingModel


class FakeClient:
    def __init__(self, fail=None):
        self.calls = []
        self.fail = fail

    def embed(self, model, input):
        self.calls.append((model, input))
        if self.fail:
            raise Exception(self.fail)
        items = [input] if isinstance(input, str) else list(input)
        return {"embeddings": [[float(len(t)), 1.0, 0.5] for t in items]}


class OllamaEmbeddingTests(unittest.TestCase):
    def test_single_embedding(self):
        client = FakeClient()
        model = OllamaEmbeddingModel("nomic-embed-text", client=client)
        self.assertEqual(model.embed("abcd"), [4.0, 1.0, 0.5])
        self.assertEqual(model.embed_query("ab"), [2.0, 1.0, 0.5])
        self.assertEqual(client.calls[0][0], "nomic-embed-text")

    def test_documents_are_batched_and_ordered(self):
        client = FakeClient()
        model = OllamaEmbeddingModel("m", client=client)
        docs = ["x" * (i + 1) for i in range(BATCH_SIZE + 5)]
        vectors = model.embed_documents(docs)
        self.assertEqual(len(vectors), len(docs))
        self.assertEqual([v[0] for v in vectors], [float(i + 1) for i in range(len(docs))])
        self.assertEqual(len(client.calls), 2)

    def test_missing_model_gives_helpful_error(self):
        model = OllamaEmbeddingModel("nomic-embed-text", client=FakeClient(fail="model 'nomic-embed-text' not found"))
        with self.assertRaises(RuntimeError) as ctx:
            model.embed("hi")
        self.assertIn("ollama pull nomic-embed-text", str(ctx.exception))

    def test_other_errors_pass_through(self):
        model = OllamaEmbeddingModel("m", client=FakeClient(fail="connection refused"))
        with self.assertRaises(Exception) as ctx:
            model.embed("hi")
        self.assertIn("connection refused", str(ctx.exception))

    def test_factory_rejects_unknown_provider(self):
        with self.assertRaises(ValueError):
            build_embedding_model("nope")


if __name__ == "__main__":
    unittest.main()
