from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import ChatSession, ChatMessage

class Session:
	def __init__(self, db: AsyncSession):
		self.db = db

	async def get_or_create_session(self, session_id: Optional[str]) -> ChatSession:
		if session_id:
			result = await self.db.execute(select(ChatSession).where(ChatSession.id == session_id))
			session = result.scalar_one_or_none()
			if session:
				return session
		
		session = ChatSession()
		self.db.add(session)
		await self.db.flush()
		return session

	async def add_message(self, session_id: str, role: str, content: str) -> ChatMessage:
		message = ChatMessage(session_id=session_id, role=role, content=content)
		self.db.add(message)
		await self.db.flush()
		return message

	async def list_messages(self, session_id: str) -> List[ChatMessage]:
		result = await self.db.execute(select(ChatMessage).where(ChatMessage.session_id == session_id).order_by(ChatMessage.created_at.asc()))
		return list(result.scalars())

