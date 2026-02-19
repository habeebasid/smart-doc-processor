"""Generate embeddings using Voyage AI"""

import os
import voyageai
from typing import List
import time


class EmbeddingService:
    """Generates vector embeddings for text"""

    def __init__(self, api_key: str = None, model: str = "voyage-2"):
        """Initialize embedding service"""
        self.api_key = api_key or os.getenv("VOYAGE_API_KEY")
        self.model = model
        print(
            f"🔑 Using Voyage API key: {self.api_key[:10]}..."
            if self.api_key
            else "❌ No API key found"
        )
        self.client = voyageai.Client(api_key=self.api_key)

    def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text"""
        result = self.client.embed([text], model=self.model)
        return result.embeddings[0]

    def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for multiple texts (more efficient)"""
        print(f"📡 Calling Voyage API for {len(texts)} texts...")
        start = time.time()

        try:
            result = self.client.embed(texts, model=self.model)
            elapsed = time.time() - start
            print(f"✅ Got embeddings in {elapsed:.2f}s")
            return result.embeddings
        except Exception as e:
            print(f"❌ Voyage API error: {e}")
            raise
