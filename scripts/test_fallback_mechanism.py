#!/usr/bin/env python3
"""
Test script for the enhanced fallback mechanism:
1. Test specific FAQ knowledge (should use context)
2. Test general knowledge (should use Gemini fallback)
3. Test escalation scenarios (should escalate to human)
"""

import asyncio
import json
import requests
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_specific_knowledge():
    """Test questions that should be answered from FAQ knowledge base."""
    print("📚 Testing Specific Knowledge (FAQ-based answers)")
    print("=" * 60)
    

    specific_questions = [
        "How do I reset my password?",
        "What are your business hours?",
        "How can I contact customer support?",
        "What is your refund policy?"
    ]
    
    session_id = None
    
    for i, question in enumerate(specific_questions, 1):
        print(f"\n🔍 Question {i}: {question}")
        
        chat_data = {
            "message": question,
            "include_suggestions": True,
            "include_summary": False
        }
        
        if session_id:
            chat_data["session_id"] = session_id
            
        response = requests.post(f"{BASE_URL}/chat", json=chat_data)
        
        if response.status_code == 200:
            result = response.json()
            session_id = result["session_id"]
            
            print(f"✅ Response: {result['response']}")
            print(f"📊 Escalated: {result['escalated']}")
            
            if result.get("next_actions"):
                print("🎯 Actions:")
                for action in result["next_actions"][:3]:
                    print(f"   • {action}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    
    return session_id

def test_general_knowledge():
    """Test questions that should use Gemini's general knowledge."""
    print(f"\n🌐 Testing General Knowledge (Gemini fallback)")
    print("=" * 60)
    
 
    general_questions = [
        "What is artificial intelligence?",
        "How does machine learning work?",
        "What are the benefits of cloud computing?",
        "Can you explain blockchain technology?"
    ]
    
    session_id = None
    
    for i, question in enumerate(general_questions, 1):
        print(f"\n🔍 Question {i}: {question}")
        
        chat_data = {
            "message": question,
            "include_suggestions": True,
            "include_summary": False
        }
        
        if session_id:
            chat_data["session_id"] = session_id
            
        response = requests.post(f"{BASE_URL}/chat", json=chat_data)
        
        if response.status_code == 200:
            result = response.json()
            session_id = result["session_id"]
            
            print(f"✅ Response: {result['response'][:200]}...") 
            print(f"📊 Escalated: {result['escalated']}")
            
            if result.get("next_actions"):
                print("🎯 Actions:")
                for action in result["next_actions"][:3]:
                    print(f"   • {action}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    
    return session_id

def test_escalation_scenarios():
    """Test questions that should escalate to human agents."""
    print(f"\n🚨 Testing Escalation Scenarios")
    print("=" * 60)
    
   
    escalation_questions = [
        "I need to cancel my order #12345 immediately",
        "There's a bug in your system that's charging me twice",
        "I want to speak to your manager about a complaint",
        "Can you access my personal account information and make changes?"
    ]
    
    session_id = None
    
    for i, question in enumerate(escalation_questions, 1):
        print(f"\n🔍 Question {i}: {question}")
        
        chat_data = {
            "message": question,
            "include_suggestions": True,
            "include_summary": False
        }
        
        if session_id:
            chat_data["session_id"] = session_id
            
        response = requests.post(f"{BASE_URL}/chat", json=chat_data)
        
        if response.status_code == 200:
            result = response.json()
            session_id = result["session_id"]
            
            print(f"✅ Response: {result['response']}")
            print(f"📊 Escalated: {result['escalated']}")
            
            if result.get("escalation_reason"):
                print(f"⚠️  Reason: {result['escalation_reason']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    
    return session_id

def test_mixed_conversation():
    """Test a mixed conversation with different types of questions."""
    print(f"\n🔄 Testing Mixed Conversation Flow")
    print("=" * 60)
    
    mixed_questions = [
        "Hello, I need help",  
        "What is your refund policy?",  
        "How does AI work?",  
        "I need to cancel my subscription immediately",  
        "Can you explain cloud computing?",  
    ]
    
    session_id = None
    
    for i, question in enumerate(mixed_questions, 1):
        print(f"\n🔍 Question {i}: {question}")
        
        chat_data = {
            "message": question,
            "include_suggestions": True,
            "include_summary": i >= 4  
        }
        
        if session_id:
            chat_data["session_id"] = session_id
            
        response = requests.post(f"{BASE_URL}/chat", json=chat_data)
        
        if response.status_code == 200:
            result = response.json()
            session_id = result["session_id"]
            
            print(f"✅ Response: {result['response'][:150]}...")
            print(f"📊 Escalated: {result['escalated']}")
            
            if result.get("conversation_summary"):
                print(f"📋 Summary: {result['conversation_summary'][:100]}...")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
    
    return session_id

def main():
    """Run all fallback mechanism tests."""
    print("🚀 Testing Enhanced Fallback Mechanism")
    print("=" * 70)
   
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code != 200:
            print("❌ Server is not running. Please start the server first.")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the server first.")
        return

    test_specific_knowledge()
    test_general_knowledge()
    test_escalation_scenarios()
    test_mixed_conversation()
    
    print(f"\n🎉 All fallback mechanism tests completed!")
    print("\n📋 Test Summary:")
    print("   • Specific Knowledge: Should use FAQ context")
    print("   • General Knowledge: Should use Gemini fallback")
    print("   • Escalation Scenarios: Should escalate to human")
    print("   • Mixed Conversation: Should handle all types appropriately")
    
    print("\n🔧 Fallback Flow:")
    print("   1. Check FAQ knowledge base")
    print("   2. If no good match → Use Gemini for general knowledge")
    print("   3. If Gemini can't help → Escalate to human agent")

if __name__ == "__main__":
    main()
