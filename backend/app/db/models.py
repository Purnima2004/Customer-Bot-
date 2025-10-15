import uuid
from datetime import datetime, timedelta
from sqlalchemy import Column, String, DateTime, ForeignKey, Text, Boolean, Integer
from sqlalchemy.orm import relationship
from app.db.session import Base

class ChatSession(Base):
	__tablename__ = "chat_sessions"

	id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
	created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
	updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
	expires_at = Column(DateTime, nullable=True)  # Session expiration
	is_active = Column(Boolean, default=True, nullable=False)
	message_count = Column(Integer, default=0, nullable=False)
	last_activity = Column(DateTime, default=datetime.utcnow, nullable=False)

	messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")

class ChatMessage(Base):
	__tablename__ = "chat_messages"

	id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
	session_id = Column(String, ForeignKey("chat_sessions.id", ondelete="CASCADE"), nullable=False)
	role = Column(String, nullable=False)  # user|assistant|system
	content = Column(Text, nullable=False)
	created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

	session = relationship("ChatSession", back_populates="messages")

