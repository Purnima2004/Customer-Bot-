from typing import List, Tuple
from pinecone import Pinecone, ServerlessSpec
from app.config import settings

class VectorStore:
	def __init__(self):
		self.pc = Pinecone(api_key=settings.pinecone_api_key)
		self.index_name = settings.pinecone_index
		self._ensure_index()
		self.index = self.pc.Index(self.index_name)

	def _ensure_index(self):
		if self.index_name not in [i.name for i in self.pc.list_indexes()]:
			self.pc.create_index(
				name=self.index_name,
				dimension=768,  
				metric="cosine",
				spec=ServerlessSpec(cloud="aws", region="us-east-1"),
			)

	async def upsert_faqs(self, ids: List[str], vectors: List[List[float]], metadatas: List[dict]):
		items = [{"id": i, "values": v, "metadata": m} for i, v, m in zip(ids, vectors, metadatas)]
		self.index.upsert(vectors=items)

	async def query(self, vector: List[float], top_k: int) -> List[Tuple[float, dict]]:
		res = self.index.query(vector=vector, top_k=top_k, include_metadata=True)
		return [(m.score, m.metadata or {}) for m in res.matches]


