from pydantic import BaseModel
from typing import List, Optional

class IngestFAQItem(BaseModel):
	question: str
	answer: str

class IngestFAQRequest(BaseModel):
	items: List[IngestFAQItem]

class ChatRequest(BaseModel):
	session_id: Optional[str] = None
	message: str
	include_suggestions: bool = True
	include_summary: bool = False

class ChatResponse(BaseModel):
	session_id: str
	response: str
	escalated: bool = False
	escalation_reason: Optional[str] = None
	conversation_summary: Optional[str] = None
	next_actions: Optional[List[str]] = None
	response_type: str = "faq" 
	confidence_score: Optional[float] = None

class SummaryRequest(BaseModel):
	session_id: str

class SummaryResponse(BaseModel):
	session_id: str
	summary: str

class ActionsRequest(BaseModel):
	session_id: str
	query: Optional[str] = None

class ActionsResponse(BaseModel):
	session_id: str
	actions: List[str]

