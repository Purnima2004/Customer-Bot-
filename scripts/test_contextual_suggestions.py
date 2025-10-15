#!/usr/bin/env python3
"""
Test script for contextual action suggestions:
- Test different question types to see if suggestions are relevant
- Verify suggestions are follow-up questions related to the original query
"""

import asyncio
import json
import requests
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

def test_account_related_suggestions():
    """Test suggestions for account-related questions."""
    print("👤 Testing Account-Related Suggestions")
    print("=" * 50)
    
    account_questions = [
        "How do I create an account?",
        "I can't access my account",
        "How do I change my account settings?",
        "I want to delete my account"
    ]
    
    for i, question in enumerate(account_questions, 1):
        print(f"\n🔍 Question {i}: {question}")
        
        chat_data = {
            "message": question,
            "include_suggestions": True,
            "include_summary": False
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=chat_data)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Response: {result['response'][:100]}...")
            print(f"📊 Response Type: {result.get('response_type', 'unknown')}")
            
            if result.get("next_actions"):
                print("🎯 Contextual Suggestions:")
                for j, action in enumerate(result["next_actions"], 1):
                    print(f"   {j}. {action}")
            else:
                print("❌ No suggestions provided")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")

def test_password_related_suggestions():
    """Test suggestions for password-related questions."""
    print(f"\n🔐 Testing Password-Related Suggestions")
    print("=" * 50)
    
    password_questions = [
        "I forgot my password",
        "How do I reset my password?",
        "My password isn't working",
        "How do I change my password?"
    ]
    
    for i, question in enumerate(password_questions, 1):
        print(f"\n🔍 Question {i}: {question}")
        
        chat_data = {
            "message": question,
            "include_suggestions": True,
            "include_summary": False
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=chat_data)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Response: {result['response'][:100]}...")
            print(f"📊 Response Type: {result.get('response_type', 'unknown')}")
            
            if result.get("next_actions"):
                print("🎯 Contextual Suggestions:")
                for j, action in enumerate(result["next_actions"], 1):
                    print(f"   {j}. {action}")
            else:
                print("❌ No suggestions provided")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")

def test_billing_related_suggestions():
    """Test suggestions for billing-related questions."""
    print(f"\n💳 Testing Billing-Related Suggestions")
    print("=" * 50)
    
    billing_questions = [
        "How do I update my payment method?",
        "I was charged twice",
        "How do I cancel my subscription?",
        "Can I get a refund?"
    ]
    
    for i, question in enumerate(billing_questions, 1):
        print(f"\n🔍 Question {i}: {question}")
        
        chat_data = {
            "message": question,
            "include_suggestions": True,
            "include_summary": False
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=chat_data)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Response: {result['response'][:100]}...")
            print(f"📊 Response Type: {result.get('response_type', 'unknown')}")
            
            if result.get("next_actions"):
                print("🎯 Contextual Suggestions:")
                for j, action in enumerate(result["next_actions"], 1):
                    print(f"   {j}. {action}")
            else:
                print("❌ No suggestions provided")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")

def test_technical_support_suggestions():
    """Test suggestions for technical support questions."""
    print(f"\n🔧 Testing Technical Support Suggestions")
    print("=" * 50)
    
    tech_questions = [
        "The app is not loading",
        "I'm getting an error message",
        "How do I contact technical support?",
        "The website is down"
    ]
    
    for i, question in enumerate(tech_questions, 1):
        print(f"\n🔍 Question {i}: {question}")
        
        chat_data = {
            "message": question,
            "include_suggestions": True,
            "include_summary": False
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=chat_data)
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Response: {result['response'][:100]}...")
            print(f"📊 Response Type: {result.get('response_type', 'unknown')}")
            
            if result.get("next_actions"):
                print("🎯 Contextual Suggestions:")
                for j, action in enumerate(result["next_actions"], 1):
                    print(f"   {j}. {action}")
            else:
                print("❌ No suggestions provided")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")

def test_conversation_flow():
    """Test how suggestions evolve during a conversation."""
    print(f"\n🔄 Testing Conversation Flow Suggestions")
    print("=" * 50)
    
    conversation_flow = [
        "I need help with my account",
        "I can't log in",
        "I forgot my password",
        "The reset email didn't arrive"
    ]
    
    session_id = None
    
    for i, question in enumerate(conversation_flow, 1):
        print(f"\n🔍 Message {i}: {question}")
        
        chat_data = {
            "message": question,
            "include_suggestions": True,
            "include_summary": i >= 3
        }
        
        if session_id:
            chat_data["session_id"] = session_id
        
        response = requests.post(f"{BASE_URL}/chat", json=chat_data)
        
        if response.status_code == 200:
            result = response.json()
            session_id = result["session_id"]
            
            print(f"✅ Response: {result['response'][:100]}...")
            print(f"📊 Response Type: {result.get('response_type', 'unknown')}")
            
            if result.get("next_actions"):
                print("🎯 Contextual Suggestions:")
                for j, action in enumerate(result["next_actions"], 1):
                    print(f"   {j}. {action}")
            else:
                print("❌ No suggestions provided")
                
            if result.get("conversation_summary"):
                print(f"📋 Summary: {result['conversation_summary'][:100]}...")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")

def analyze_suggestion_quality():
    """Analyze the quality and relevance of suggestions."""
    print(f"\n📊 Analyzing Suggestion Quality")
    print("=" * 50)
    
    test_cases = [
        {
            "question": "How do I create an account?",
            "expected_topics": ["account", "registration", "signup", "create"],
            "category": "Account Management"
        },
        {
            "question": "I forgot my password",
            "expected_topics": ["password", "reset", "recovery", "login"],
            "category": "Password Issues"
        },
        {
            "question": "How do I cancel my subscription?",
            "expected_topics": ["cancel", "subscription", "billing", "payment"],
            "category": "Billing"
        }
    ]
    
    for test_case in test_cases:
        print(f"\n🧪 Testing: {test_case['question']}")
        print(f"📂 Category: {test_case['category']}")
        
        chat_data = {
            "message": test_case["question"],
            "include_suggestions": True,
            "include_summary": False
        }
        
        response = requests.post(f"{BASE_URL}/chat", json=chat_data)
        
        if response.status_code == 200:
            result = response.json()
            
            if result.get("next_actions"):
                print("🎯 Generated Suggestions:")
                relevance_score = 0
                total_suggestions = len(result["next_actions"])
                
                for j, action in enumerate(result["next_actions"], 1):
                    print(f"   {j}. {action}")
                    
                    # Check if suggestion contains expected topics
                    action_lower = action.lower()
                    for topic in test_case["expected_topics"]:
                        if topic.lower() in action_lower:
                            relevance_score += 1
                            break
                
                relevance_percentage = (relevance_score / total_suggestions) * 100
                print(f"📈 Relevance Score: {relevance_score}/{total_suggestions} ({relevance_percentage:.1f}%)")
                
                if relevance_percentage >= 80:
                    print("✅ Excellent contextual relevance")
                elif relevance_percentage >= 60:
                    print("✅ Good contextual relevance")
                else:
                    print("⚠️ Suggestions could be more relevant")
            else:
                print("❌ No suggestions provided")
        else:
            print(f"❌ Error: {response.status_code} - {response.text}")

def main():
    """Run all contextual suggestion tests."""
    print("🚀 Testing Contextual Action Suggestions")
    print("=" * 70)
    
   
    try:
        response = requests.get(f"{BASE_URL}/docs")
        if response.status_code != 200:
            print("❌ Server is not running. Please start the server first.")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Please start the server first.")
        return
    
    # Run all tests
    test_account_related_suggestions()
    test_password_related_suggestions()
    test_billing_related_suggestions()
    test_technical_support_suggestions()
    test_conversation_flow()
    analyze_suggestion_quality()
    
    print(f"\n🎉 All contextual suggestion tests completed!")
    print("\n📋 Test Summary:")
    print("   • Account-related questions should suggest account management follow-ups")
    print("   • Password questions should suggest password recovery options")
    print("   • Billing questions should suggest payment/subscription actions")
    print("   • Technical questions should suggest troubleshooting steps")
    print("   • Suggestions should evolve based on conversation context")
    print("   • Suggestions should be natural follow-up questions")
    
    print("\n🎯 Expected Behavior:")
    print("   • Suggestions should be contextually relevant to the user's question")
    print("   • Suggestions should sound like natural follow-up questions")
    print("   • Suggestions should help users explore related topics")
    print("   • Suggestions should be actionable and specific")

if __name__ == "__main__":
    main()

