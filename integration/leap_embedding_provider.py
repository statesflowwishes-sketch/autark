from .leap_client import LeapClient
import hashlib

class LeapEmbeddingProvider:
    def __init__(self, cache, client: LeapClient):
        self.cache = cache
        self.client = client

    def embed_batch(self, texts, model="embed-v1"):
        to_query = []
        mapping = []
        results = []
        for t in texts:
            key = f"emb:{model}:{hashlib.sha256(t.encode()).hexdigest()}"
            cached = self.cache.get(key)
            if cached:
                results.append(cached)
            else:
                mapping.append((t, key))
                to_query.append(t)
        if to_query:
            embeddings = self.client.embed(to_query, model=model)
            for (t, key), emb in zip(mapping, embeddings):
                self.cache.set(key, emb)
                results.append(emb)
        return results