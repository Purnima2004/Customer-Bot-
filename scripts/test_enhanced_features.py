#!/usr/bin/env python3
"""
Test script for the enhanced bot features:
- Generate responses
- Summarize conversations  
- Suggest next actions
"""

import asyncio
import json
import requests
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_chat_with_enhanced_features():
    """Test the enhanced chat endpoint with all new features."""
    print("🤖 Testing Enhanced Chat Features")
    print("=" * 50)
    
    session_id = None
    
    # Test messages to create a conversation
    test_messages = [
        "Hello, I'm having trouble with my account login",
        "I keep getting an error message when I try to reset my password",
        "The error says 'Invalid email format' but my email is correct",
        "Can you help me understand what might be wrong?"
    ]
    
    for i, message in enumerate(test_messages, 1):
        print(f"\n📝 Message {i}: {message}")
        
        # Make chat request with enhanced features
        chat_data = {
            "message": message,
            "include_suggestions": True,
            "include_summary": i >= 3  # Include summary for longer conversations
        }
        
        if session_id:
            chat_data["session_id"] = session_id
            
        response = requests.post(f"{BASE_URL}/chat", json=chat_data)
        
        if response.status_code == 200:
            result = response.json()
            session_id = result["session_id"]
            
            print(f"✅ Response: {result['response']}")
            
            if result.get("next_actions"):
                print("🎯 Next Actions:")
                for action in result["next_actions"]:
                    print(f"   • {action}")
            
            if result.get("conversation_summary"):
                print("📋 Conversation Summary:")
                print(f"   {result['conversation_summary']}")
                
            if result.get("escalated"):
                print(f"⚠️  Escalated: {result['escalation_reason']}")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")
            return False
    
    return session_id

def test_standalone_summarization(session_id: str):
    """Test the standalone conversation summarization endpoint."""
    print(f"\n📋 Testing Standalone Summarization")
    print("=" * 50)
    
    summary_data = {"session_id": session_id}
    response = requests.post(f"{BASE_URL}/summarize", json=summary_data)
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Summary: {result['summary']}")
        return True
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return False

def test_standalone_action_suggestions(session_id: str):
    """Test the standalone action suggestions endpoint."""
    print(f"\n🎯 Testing Standalone Action Suggestions")
    print("=" * 50)
    
    actions_data = {"session_id": session_id}
    response = requests.post(f"{BASE_URL}/suggest-actions", json=actions_data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Suggested Actions:")
        for action in result["actions"]:
            print(f"   • {action}")
        return True
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return False

def test_action_suggestions_with_query(session_id: str):
    """Test action suggestions with a specific query."""
    print(f"\n🎯 Testing Action Suggestions with Specific Query")
    print("=" * 50)
    
    actions_data = {
        "session_id": session_id,
        "query": "I want to upgrade my account to premium"
    }
    response = requests.post(f"{BASE_URL}/suggest-actions", json=actions_data)
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Suggested Actions for 'upgrade to premium':")
        for action in result["actions"]:
            print(f"   • {action}")
        return True
    else:
        print(f"❌ Error: {response.status_code} - {response.text}")
        return False

def main():
    """Run all tests."""
    print("🚀 Testing Enhanced Bot Features")
    print("=" * 60)
    
    # Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code != 200:
            print("❌ Server is not running. Please start the server first.")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the server first.")
        return
    
    # Test enhanced chat features
    session_id = test_chat_with_enhanced_features()
    
    if not session_id:
        print("❌ Chat test failed. Cannot continue with other tests.")
        return
    
    # Test standalone features
    test_standalone_summarization(session_id)
    test_standalone_action_suggestions(session_id)
    test_action_suggestions_with_query(session_id)
    
    print(f"\n🎉 All tests completed! Session ID: {session_id}")
    print("\n📚 API Endpoints Available:")
    print("   • POST /chat - Enhanced chat with optional summary and suggestions")
    print("   • POST /summarize - Get conversation summary")
    print("   • POST /suggest-actions - Get next action suggestions")

if __name__ == "__main__":
    main()
