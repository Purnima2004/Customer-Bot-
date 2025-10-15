from typing import List, Tuple, Optional
import google.generativeai as genai
from app.config import settings
from app.services.embeddings import Embeddings
from app.services.vector_store import VectorStore
from app.prompts.templates import prompt_manager, PromptType
from app.exceptions import LLMServiceException, VectorStoreException, EmbeddingException
from app.utils.logger import logger


class RAG:
    def __init__(self):
        self.emb = Embeddings()
        self.store = VectorStore()

        # Configuring Gemini
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel(model_name=settings.chat_model)

    async def retrieve(self, query: str) -> List[Tuple[float, dict]]:
        try:
            emb = await self.emb.embed_text(query)
            return await self.store.query(emb, settings.top_k)
        except Exception as e:
            logger.log_error(e, {"operation": "retrieve", "query": query})
            raise VectorStoreException(f"Failed to retrieve context: {str(e)}", "retrieve")

    async def build_context(self, query: str) -> tuple[str, bool, float]:
        matches = await self.retrieve(query)
        if not matches:
            return "", True, 0.0

        best_score = matches[0][0]
        should_escalate = best_score < settings.score_threshold

        context_parts, chars = [], 0
        for score, meta in matches:
            qa = f"Q: {meta.get('question', '')}\nA: {meta.get('answer', '')}\n"
            if chars + len(qa) > settings.max_context_chars:
                break
            context_parts.append(qa)
            chars += len(qa)

        context = "\n".join(context_parts)
        return context, should_escalate, best_score

    async def answer(self, query: str, chat_history: List[dict]) -> tuple[str, bool, float, str]:
        context, should_escalate, score = await self.build_context(query)
      
        trimmed_history = chat_history[-6:] if len(chat_history) > 6 else chat_history

        # Answering using the provided context/FAQ
        if context and not should_escalate:
            if score >= 0.90:
                try:
                    # Return the answer of the best match without LLM call
                    best_answer = context.split("A:", 1)[1].strip().split("\n")[0] if "A:" in context else None
                    if best_answer:
                        return best_answer, False, score, "faq"
                except Exception:
                    pass
            try:
              
                history_text = "\n".join(
                    [f"{m['role']}: {m['content']}" for m in trimmed_history]
                )

              
                full_prompt = prompt_manager.get_prompt(
                    PromptType.FAQ_RESPONSE,
                    context=context,
                    conversation_history=history_text,
                    user_question=query
                )

                # Generate answer using Gemini
                response = self.model.generate_content(full_prompt)
                answer = response.text.strip()
                return answer, False, score, "faq"
            except Exception as e:
                logger.log_error(e, {"operation": "faq_response", "query": query})
                raise LLMServiceException(f"Failed to generate FAQ response: {str(e)}", settings.chat_model)

        # If no good context or low confidence, try Gemini for general knowledge
        else:
            general_answer, general_escalate = await self.get_general_answer(query, trimmed_history)
            if not general_escalate:
                return general_answer, False, score, "general"
            else:
                # Final fallback - escalate to human
                return (
                    "I apologize, but I'm unable to provide a specific answer to your question. "
                    "Let me connect you with a human agent who can better assist you.",
                    True,
                    score,
                    "escalated"
                )

    async def get_general_answer(self, query: str, chat_history: List[dict]) -> tuple[str, bool]:
        """Get a general answer from Gemini when specific knowledge is not available."""
        try:
            # Build conversation history for Gemini
            history_text = "\n".join(
                [f"{m['role']}: {m['content']}" for m in chat_history]
            )

            # Use prompt template
            full_prompt = prompt_manager.get_prompt(
                PromptType.GENERAL_RESPONSE,
                conversation_history=history_text,
                user_question=query
            )

            response = self.model.generate_content(full_prompt)
            answer = response.text.strip()
        
            if "ESCALATE_TO_HUMAN" in answer.upper() or "escalate" in answer.lower():
                return answer, True
            
            return answer, False
            
        except Exception as e:
            logger.log_error(e, {"operation": "general_response", "query": query})
            raise LLMServiceException(f"Failed to generate general response: {str(e)}", settings.chat_model)

    async def summarize_conversation(self, chat_history: List[dict]) -> str:
        """Generate a summary of the conversation history."""
        if not chat_history:
            return "No conversation to summarize."
        
        try:
            conversation_text = "\n".join(
                [f"{m['role'].title()}: {m['content']}" for m in chat_history]
            )
            
            summary_prompt = prompt_manager.get_prompt(
                PromptType.CONVERSATION_SUMMARY,
                conversation_text=conversation_text
            )
            
            response = self.model.generate_content(summary_prompt)
            return response.text.strip()
        except Exception as e:
            logger.log_error(e, {"operation": "conversation_summary"})
            raise LLMServiceException(f"Failed to generate conversation summary: {str(e)}", settings.chat_model)

    async def suggest_next_actions(self, query: str, chat_history: List[dict], context: str = "") -> List[str]:
        """Suggest contextually relevant next actions based on the user's specific question."""
        clipped_history = chat_history[-5:] if len(chat_history) > 5 else chat_history
        conversation_text = "\n".join(
            [f"{m['role'].title()}: {m['content']}" for m in clipped_history]
        )
        
      
        try:
            topic_prompt = prompt_manager.get_prompt(
                PromptType.TOPIC_ANALYSIS,
                user_question=query
            )
            topic_response = self.model.generate_content(topic_prompt)
            main_topic = topic_response.text.strip().lower()
        except Exception as e:
            logger.log_error(e, {"operation": "topic_analysis", "query": query})
            main_topic = "general support"
        
        try:
            actions_prompt = prompt_manager.get_prompt(
                PromptType.ACTION_SUGGESTIONS,
                user_question=query,
                main_topic=main_topic,
                conversation_context=conversation_text,
                faq_context=context
            )
            
            response = self.model.generate_content(actions_prompt)
            actions = [action.strip() for action in response.text.strip().split('\n') if action.strip()]
            
            filtered_actions = []
            for action in actions:
                if len(action) > 10 and not action.lower().startswith(('here', 'you can', 'please', 'thank')):
                    filtered_actions.append(action)
            
            return filtered_actions[:5]  
            
        except Exception as e:
            logger.log_error(e, {"operation": "action_suggestions", "query": query})
            return [
                "Can you provide more details about your specific situation?",
                "Would you like me to walk you through the steps?",
                "Do you need help with anything else related to this?",
                "Is there a specific part you're having trouble with?"
            ]

    async def generate_enhanced_response(self, query: str, chat_history: List[dict], include_suggestions: bool = True) -> Tuple[str, bool, float, Optional[str], Optional[List[str]], str]:
        """Generate an enhanced response with optional conversation summary and action suggestions."""
   
        answer, should_escalate, score, response_type = await self.answer(query, chat_history)
        
        summary = None
        suggestions = None
        
        if len(chat_history) >= 4:  
            summary = await self.summarize_conversation(chat_history)
        

        if include_suggestions and not should_escalate:
          
            context, _, _ = await self.build_context(query)
            suggestions = await self.suggest_next_actions(query, chat_history, context)
        
        return answer, should_escalate, score, summary, suggestions, response_type
