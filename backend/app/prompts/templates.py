"""
Prompt templates for the Customer Bot application.
Provides structured and maintainable prompt engineering.
"""

from typing import List, Dict, Optional
from enum import Enum


class PromptType(Enum):
    """Types of prompts available."""
    FAQ_RESPONSE = "faq_response"
    GENERAL_RESPONSE = "general_response"
    CONVERSATION_SUMMARY = "conversation_summary"
    ACTION_SUGGESTIONS = "action_suggestions"
    TOPIC_ANALYSIS = "topic_analysis"
    ESCALATION_DETECTION = "escalation_detection"


class PromptTemplate:
    """Base class for prompt templates."""
    
    def __init__(self, template: str, variables: List[str]):
        self.template = template
        self.variables = variables
    
    def format(self, **kwargs) -> str:
        """Format the template with provided variables."""
        # Check if all required variables are provided
        missing_vars = set(self.variables) - set(kwargs.keys())
        if missing_vars:
            raise ValueError(f"Missing required variables: {missing_vars}")
        
        return self.template.format(**kwargs)


class PromptManager:
    """Manages all prompt templates for the application."""
    
    def __init__(self):
        self.templates = {
            PromptType.FAQ_RESPONSE: PromptTemplate(
                template="""You are a helpful customer support assistant. Your role is to provide accurate, helpful, and specific information to customers based on the provided FAQ knowledge base.

Context from FAQ knowledge base:
{context}

Conversation history:
{conversation_history}

User question: {user_question}

Instructions:
1. Use the provided FAQ context to answer the user's question
2. Be specific and actionable in your response
3. If the context doesn't fully answer the question, acknowledge this and provide the best available information
4. Maintain a helpful and professional tone
5. If multiple FAQ items are relevant, synthesize them into a comprehensive answer

Please provide a helpful response:""",
                variables=["context", "conversation_history", "user_question"]
            ),
            
            PromptType.GENERAL_RESPONSE: PromptTemplate(
                template="""You are a helpful customer support assistant. The user has asked a question that may not be fully covered in our specific knowledge base.

Conversation history:
{conversation_history}

User question: {user_question}

Instructions:
1. Provide a helpful, general answer based on your knowledge
2. Be honest about limitations if the question requires specific internal information
3. Suggest appropriate next steps when possible
4. If the question is too specific to our business or requires access to internal systems, respond with 'ESCALATE_TO_HUMAN'
5. Maintain a professional and helpful tone

Please provide a helpful response:""",
                variables=["conversation_history", "user_question"]
            ),
            
            PromptType.CONVERSATION_SUMMARY: PromptTemplate(
                template="""Please provide a concise summary of this customer support conversation. Focus on the main issues discussed, questions asked, and solutions provided.

Conversation:
{conversation_text}

Instructions:
1. Identify the main customer issue or question
2. Summarize the key points discussed
3. Note any solutions or recommendations provided
4. Keep the summary under 200 words
5. Use clear, professional language

Summary:""",
                variables=["conversation_text"]
            ),
            
            PromptType.ACTION_SUGGESTIONS: PromptTemplate(
                template="""Based on the user's question and conversation context, generate contextually relevant follow-up questions and actions.

User question: {user_question}
Main topic: {main_topic}
Conversation context: {conversation_context}
Available FAQ context: {faq_context}

Instructions:
Generate 4-5 contextually relevant follow-up questions and actions that a customer would likely ask next about this specific topic. Focus on:
- Natural follow-up questions related to their specific issue
- Alternative approaches to solve their problem
- Related concerns they might have
- Next steps they might need to take
- Additional information they might need

Make the suggestions sound like natural questions a real customer would ask. Format as complete questions or actionable statements.

Examples for different topics:
- Account issues: 'How do I change my account settings?', 'Can I have multiple accounts?', 'How do I deactivate my account?'
- Password issues: 'What if I don't receive the reset email?', 'How do I create a stronger password?', 'Can I change my security questions?'
- Billing issues: 'How do I update my payment method?', 'Can I get a refund?', 'How do I view my billing history?'
- Technical issues: 'What browsers are supported?', 'How do I clear my cache?', 'Is there a mobile app?'

Generate 4-5 relevant suggestions (one per line, no numbering):""",
                variables=["user_question", "main_topic", "conversation_context", "faq_context"]
            ),
            
            PromptType.TOPIC_ANALYSIS: PromptTemplate(
                template="""Analyze this user question and identify the main topic/domain: '{user_question}'

Identify the key topic (e.g., 'account management', 'password reset', 'billing', 'technical support', etc.)

Respond with just the main topic in 2-3 words.""",
                variables=["user_question"]
            ),
            
            PromptType.ESCALATION_DETECTION: PromptTemplate(
                template="""Analyze this customer support interaction to determine if it should be escalated to a human agent.

User question: {user_question}
Conversation context: {conversation_context}
Available FAQ context: {faq_context}

Consider escalating if:
1. The question requires access to specific internal systems or databases
2. The customer is expressing frustration or anger
3. The question involves sensitive personal information
4. The FAQ context doesn't provide sufficient information
5. The customer explicitly requests human assistance

Respond with either 'ESCALATE' or 'CONTINUE' followed by a brief reason.""",
                variables=["user_question", "conversation_context", "faq_context"]
            )
        }
    
    def get_prompt(self, prompt_type: PromptType, **kwargs) -> str:
        """Get a formatted prompt of the specified type."""
        if prompt_type not in self.templates:
            raise ValueError(f"Unknown prompt type: {prompt_type}")
        
        template = self.templates[prompt_type]
        return template.format(**kwargs)
    
    def add_custom_prompt(self, prompt_type: PromptType, template: str, variables: List[str]):
        """Add a custom prompt template."""
        self.templates[prompt_type] = PromptTemplate(template, variables)
    
    def list_available_prompts(self) -> List[PromptType]:
        """List all available prompt types."""
        return list(self.templates.keys())


# Global prompt manager instance
prompt_manager = PromptManager()

