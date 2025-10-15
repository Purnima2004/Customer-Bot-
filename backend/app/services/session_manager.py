"""
Enhanced session management with expiration and cleanup capabilities.
"""

import asyncio
from datetime import datetime, timedelta
from typing import Optional, List
from sqlalchemy import select, update, delete, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ChatSession, ChatMessage
from app.exceptions import SessionException
from app.utils.logger import Logger
from app.config import settings


class SessionManager:
    """Enhanced session management with expiration and cleanup."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.session_timeout = timedelta(hours=24)  
        self.cleanup_interval = timedelta(hours=1)  
        self.logger = Logger().get_logger("session")
    
    async def get_or_create_session(self, session_id: Optional[str]) -> ChatSession:
        """Get existing session or create new one with expiration."""
        if session_id:
            result = await self.db.execute(
                select(ChatSession).where(
                    and_(
                        ChatSession.id == session_id,
                        ChatSession.is_active == True,
                        ChatSession.expires_at > datetime.utcnow()
                    )
                )
            )
            session = result.scalar_one_or_none()
            if session:
               
                await self._update_session_activity(session)
                return session
        
        
        session = ChatSession(
            expires_at=datetime.utcnow() + self.session_timeout
        )
        self.db.add(session)
        await self.db.flush()
        
        self.logger.info(f"Created new session: {session.id}")
        return session
    
    async def _update_session_activity(self, session: ChatSession):
        """Update session activity timestamp and extend expiration."""
        session.last_activity = datetime.utcnow()
        session.expires_at = datetime.utcnow() + self.session_timeout
        session.updated_at = datetime.utcnow()
        await self.db.flush()
    
    async def add_message(self, session_id: str, role: str, content: str) -> ChatMessage:
        """Add message to session and update counters."""
     
        result = await self.db.execute(
            select(ChatSession).where(
                and_(
                    ChatSession.id == session_id,
                    ChatSession.is_active == True
                )
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise SessionException("Session not found or expired", session_id)
        
    
        message = ChatMessage(session_id=session_id, role=role, content=content)
        self.db.add(message)
        
    
        session.message_count += 1
        session.last_activity = datetime.utcnow()
        session.updated_at = datetime.utcnow()
        
        await self.db.flush()
        return message
    
    async def list_messages(self, session_id: str) -> List[ChatMessage]:
        """List messages for active session."""

        result = await self.db.execute(
            select(ChatSession).where(
                and_(
                    ChatSession.id == session_id,
                    ChatSession.is_active == True
                )
            )
        )
        session = result.scalar_one_or_none()
        if not session:
            raise SessionException("Session not found or expired", session_id)
        
        result = await self.db.execute(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id)
            .order_by(ChatMessage.created_at.asc())
        )
        return list(result.scalars())
    
    async def deactivate_session(self, session_id: str) -> bool:
        """Deactivate a session."""
        result = await self.db.execute(
            update(ChatSession)
            .where(ChatSession.id == session_id)
            .values(is_active=False, updated_at=datetime.utcnow())
        )
        
        if result.rowcount > 0:
            self.logger.info(f"Deactivated session: {session_id}")
            return True
        return False
    
    async def cleanup_expired_sessions(self) -> int:
        """Clean up expired sessions and their messages."""
        expired_sessions = await self.db.execute(
            select(ChatSession).where(
                and_(
                    ChatSession.expires_at < datetime.utcnow(),
                    ChatSession.is_active == True
                )
            )
        )
        sessions = list(expired_sessions.scalars())
        
        if not sessions:
            return 0
        
        session_ids = [session.id for session in sessions]
        
       
        await self.db.execute(
            delete(ChatMessage).where(ChatMessage.session_id.in_(session_ids))
        )
        
       
        await self.db.execute(
            delete(ChatSession).where(ChatSession.id.in_(session_ids))
        )
        
        self.logger.info(f"Cleaned up {len(sessions)} expired sessions")
        return len(sessions)
    
    async def get_session_stats(self) -> dict:
        """Get session statistics."""
       
        active_result = await self.db.execute(
            select(ChatSession).where(ChatSession.is_active == True)
        )
        active_sessions = list(active_result.scalars())
        
       
        total_messages_result = await self.db.execute(
            select(ChatMessage)
        )
        total_messages = len(list(total_messages_result.scalars()))
        
       
        expiring_soon = [
            s for s in active_sessions 
            if s.expires_at and s.expires_at < datetime.utcnow() + timedelta(hours=1)
        ]
        
        return {
            "active_sessions": len(active_sessions),
            "total_messages": total_messages,
            "sessions_expiring_soon": len(expiring_soon),
            "average_messages_per_session": total_messages / len(active_sessions) if active_sessions else 0
        }
    
    async def start_cleanup_task(self):
        """Start background cleanup task."""
        while True:
            try:
                await asyncio.sleep(self.cleanup_interval.total_seconds())
                await self.cleanup_expired_sessions()
            except Exception as e:
                self.logger.error(
                    f"Session cleanup task error: {str(e)}",
                    exc_info=True,
                    extra={"context": "session_cleanup_task"}
                )

