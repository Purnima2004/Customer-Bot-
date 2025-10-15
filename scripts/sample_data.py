#!/usr/bin/env python3
"""
Sample FAQ data ingestion script for AI Customer Support Bot
Run this script to populate your vector database with sample FAQs
"""

import asyncio
import httpx
from typing import List, Dict

# Sample FAQ data
SAMPLE_FAQS = [
    {
        "question": "How do I reset my password?",
        "answer": "To reset your password, go to the login page and click 'Forgot Password'. Enter your email address and check your inbox for a reset link. Click the link and follow the instructions to create a new password."
    },
    {
        "question": "What are your business hours?",
        "answer": "Our customer support is available Monday through Friday from 9 AM to 6 PM EST, and Saturday from 10 AM to 4 PM EST. We are closed on Sundays and major holidays."
    },
    {
        "question": "How can I contact customer support?",
        "answer": "You can contact us through multiple channels: Email support@company.com, phone at 1-800-SUPPORT, live chat on our website, or submit a ticket through our support portal."
    },
    {
        "question": "How do I cancel my subscription?",
        "answer": "To cancel your subscription, log into your account, go to Account Settings, then Billing. Click 'Cancel Subscription' and follow the prompts. Your service will continue until the end of your current billing period."
    },
    {
        "question": "What payment methods do you accept?",
        "answer": "We accept all major credit cards (Visa, MasterCard, American Express), PayPal, and bank transfers. All payments are processed securely through our encrypted payment system."
    },
    {
        "question": "How do I update my billing information?",
        "answer": "To update your billing information, log into your account and go to Account Settings > Billing Information. You can update your credit card details, billing address, and payment method here."
    },
    {
        "question": "Is there a mobile app available?",
        "answer": "Yes, we have mobile apps available for both iOS and Android. You can download them from the App Store or Google Play Store. The mobile app provides full functionality including chat support."
    },
    {
        "question": "How do I download my data?",
        "answer": "To download your data, go to Account Settings > Privacy & Data. Click 'Request Data Download' and you'll receive an email with a secure link to download all your data within 30 days."
    },
    {
        "question": "What is your refund policy?",
        "answer": "We offer a 30-day money-back guarantee for all new subscriptions. If you're not satisfied, contact our support team within 30 days of your initial purchase for a full refund."
    },
    {
        "question": "How do I add team members to my account?",
        "answer": "To add team members, go to Account Settings > Team Management. Click 'Add Member' and enter their email address. They'll receive an invitation to join your team with the permissions you specify."
    }
]

async def ingest_faqs():
    """Ingest sample FAQ data into the vector database"""

    request_data = {
        "items": SAMPLE_FAQS
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "http://localhost:8000/api/ingest/faq",
                json=request_data,
                timeout=60.0
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Successfully ingested {result['ingested']} FAQ items!")
                print("\nSample FAQs added:")
                for i, faq in enumerate(SAMPLE_FAQS, 1):
                    print(f"{i}. {faq['question']}")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
    except httpx.ConnectError:
        print("❌ Error: Could not connect to the server.")
        print("Make sure your FastAPI server is running on http://localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting FAQ data ingestion...")
    asyncio.run(ingest_faqs())
