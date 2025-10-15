import uuid
import time
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import ChatRequest, ChatResponse, SummaryRequest, SummaryResponse, ActionsRequest, ActionsResponse
from app.db.session import get_db
from app.services.session_manager import SessionManager
from app.services.rag import RAG
from app.monitoring.metrics import metrics_collector, RequestMetrics
from app.utils.logger import logger

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(req: ChatRequest, request: Request, db: AsyncSession = Depends(get_db)):
    start_time = time.time()
    
    try:
        service = SessionManager(db)
        rag = RAG()

        session = await service.get_or_create_session(req.session_id)
        await service.add_message(session.id, role="user", content=req.message)

       
        stored = await service.list_messages(session.id)
        chat_history = [{"role": m.role, "content": m.content} for m in stored if m.role in ("user", "assistant")]


        answer, should_escalate, score, summary, suggestions, response_type = await rag.generate_enhanced_response(
            req.message, chat_history, req.include_suggestions
        )
        await service.add_message(session.id, role="assistant", content=answer)
        await db.commit()

        response_time = time.time() - start_time

       
        logger.log_chat_interaction(
            session_id=session.id,
            message=req.message,
            response=answer,
            response_time=response_time,
            confidence_score=score,
            response_type=response_type,
            escalated=should_escalate
        )

        # Record metrics
        await metrics_collector.record_request(
            RequestMetrics(
                endpoint="/api/chat",
                method="POST",
                status_code=200,
                response_time=response_time,
                timestamp=time.time(),
                session_id=session.id,
                confidence_score=score,
                response_type=response_type,
                escalated=should_escalate
            )
        )

        escalation_reason = None
        if should_escalate:
            escalation_reason = f"Low similarity score: {score:.2f}. Escalating to human agent."

       
        conversation_summary = None
        if req.include_summary and summary:
            conversation_summary = summary

        return ChatResponse(
            session_id=session.id,
            response=answer,
            escalated=should_escalate,
            escalation_reason=escalation_reason,
            conversation_summary=conversation_summary,
            next_actions=suggestions,
            response_type=response_type,
            confidence_score=score,
        )
    except Exception as e:
        response_time = time.time() - start_time
        logger.log_error(e, {
            "endpoint": "/api/chat",
            "session_id": req.session_id,
            "response_time": response_time
        })
        raise

@router.post("/summarize", response_model=SummaryResponse)
async def summarize_conversation(req: SummaryRequest, db: AsyncSession = Depends(get_db)):
    """Generate a summary of the conversation in a session."""
    try:
        service = SessionManager(db)
        rag = RAG()

       
        stored = await service.list_messages(req.session_id)
        if not stored:
            return SummaryResponse(session_id=req.session_id, summary="No conversation found for this session.")
        
        chat_history = [{"role": m.role, "content": m.content} for m in stored if m.role in ("user", "assistant")]
        summary = await rag.summarize_conversation(chat_history)
        
        logger.info(f"Generated summary for session: {req.session_id}")
        return SummaryResponse(session_id=req.session_id, summary=summary)
    except Exception as e:
        logger.log_error(e, {"endpoint": "/api/summarize", "session_id": req.session_id})
        raise

@router.post("/suggest-actions", response_model=ActionsResponse)
async def suggest_actions(req: ActionsRequest, db: AsyncSession = Depends(get_db)):
    """Suggest next actions based on the conversation history."""
    try:
        service = SessionManager(db)
        rag = RAG()

       
        stored = await service.list_messages(req.session_id)
        if not stored:
            return ActionsResponse(session_id=req.session_id, actions=["Start a conversation to get personalized suggestions."])
        
        chat_history = [{"role": m.role, "content": m.content} for m in stored if m.role in ("user", "assistant")]
        
       
        latest_user_message = req.query
        if not latest_user_message and chat_history:
           
            for msg in reversed(chat_history):
                if msg["role"] == "user":
                    latest_user_message = msg["content"]
                    break
        
        if not latest_user_message:
            latest_user_message = "How can I help you today?"
        
       
        context, _, _ = await rag.build_context(latest_user_message)
        actions = await rag.suggest_next_actions(latest_user_message, chat_history, context)
        
        logger.info(f"Generated {len(actions)} action suggestions for session: {req.session_id}")
        return ActionsResponse(session_id=req.session_id, actions=actions)
    except Exception as e:
        logger.log_error(e, {"endpoint": "/api/suggest-actions", "session_id": req.session_id})
        raise
