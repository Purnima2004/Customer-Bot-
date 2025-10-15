#!/usr/bin/env python3
"""
Test script for the AI Customer Support Bot
This script demonstrates how to interact with the chat API
"""

import asyncio
import httpx
import json
from typing import Optional

class ChatBotTester:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_id: Optional[str] = None
    
    async def send_message(self, message: str) -> dict:
        """Send a message to the chat API"""
        request_data = {
            "message": message,
            "session_id": self.session_id
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{self.base_url}/api/chat",
                json=request_data,
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                self.session_id = result["session_id"]
                return result
            else:
                raise Exception(f"API Error: {response.status_code} - {response.text}")
    
    async def chat_loop(self):
        """Interactive chat loop for testing"""
        print("🤖 AI Customer Support Bot - Test Interface")
        print("=" * 50)
        print("Type 'quit' to exit, 'clear' to start a new session")
        print()
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() == 'quit':
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'clear':
                    self.session_id = None
                    print("🔄 New session started!")
                    continue
                elif not user_input:
                    continue
                
                print("🤖 Bot is thinking...")
                response = await self.send_message(user_input)
                
                print(f"Bot: {response['response']}")
                
                if response['escalated']:
                    print(f"⚠️  ESCALATED: {response['escalation_reason']}")
                
                print("-" * 30)
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {e}")

async def test_sample_questions():
    """Test with predefined sample questions"""
    tester = ChatBotTester()
    
    sample_questions = [
        "How do I reset my password?",
        "What are your business hours?",
        "How can I contact support?",
        "I need help with something not in your FAQ",
        "How do I cancel my subscription?"
    ]
    
    print("🧪 Testing with sample questions...")
    print("=" * 50)
    
    for question in sample_questions:
        try:
            print(f"\nYou: {question}")
            response = await tester.send_message(question)
            print(f"Bot: {response['response']}")
            
            if response['escalated']:
                print(f"⚠️  ESCALATED: {response['escalation_reason']}")
            
            print("-" * 30)
            
        except Exception as e:
            print(f"❌ Error with question '{question}': {e}")

async def main():
    """Main function to choose testing mode"""
    print("Choose testing mode:")
    print("1. Interactive chat")
    print("2. Sample questions test")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        tester = ChatBotTester()
        await tester.chat_loop()
    elif choice == "2":
        await test_sample_questions()
    else:
        print("Invalid choice. Running sample questions test...")
        await test_sample_questions()

if __name__ == "__main__":
    asyncio.run(main())
