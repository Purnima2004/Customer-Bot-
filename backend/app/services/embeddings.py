from typing import List
import asyncio
from app.config import settings

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False

class Embeddings:
    def __init__(self):
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers is not available. "
                "Please install it with: pip install sentence-transformers==2.7.0"
            )
        
       
        self.model_name = settings.embedding_model
        try:
            self.client = SentenceTransformer(self.model_name)
        except Exception as e:
            raise RuntimeError(f"Failed to load embedding model '{self.model_name}': {e}")

    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        Convert a list of texts into embeddings.
        Returns a list of lists of floats (same format as OpenAI embeddings).
        """
       
        import asyncio
        loop = asyncio.get_event_loop()
        embeddings = await loop.run_in_executor(None, self.client.encode, texts)
        return embeddings.tolist()  

    async def embed_text(self, text: str) -> List[float]:
        """
        Convert a single text string into embedding.
        """
        return (await self.embed_texts([text]))[0]
