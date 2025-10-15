import uuid
from fastapi import APIRouter, HTTPException
from app.schemas import IngestFAQRequest
from app.services.embeddings import Embeddings
from app.services.vector_store import VectorStore

router = APIRouter()

@router.post("/faq")
async def ingest_faq(req: IngestFAQRequest):
	if not req.items:
		raise HTTPException(status_code=400, detail="No FAQ items provided")

	emb = Embeddings()
	store = VectorStore()

	questions = [it.question for it in req.items]
	answers = [it.answer for it in req.items]
	metadatas = [{"question": q, "answer": a} for q, a in zip(questions, answers)]
	ids = [str(uuid.uuid5(uuid.NAMESPACE_URL, q)) for q in questions]
	vectors = await emb.embed_texts([q + "\n" + a for q, a in zip(questions, answers)])

	await store.upsert_faqs(ids, vectors, metadatas)
	return {"ingested": len(ids)}
