#!/usr/bin/env python3
"""
Simple script to ingest Hugging Face dataset directly to your backend
"""

import asyncio
import httpx
from datasets import load_dataset

async def ingest_hf_dataset():
    """Load and ingest the Hugging Face dataset"""
    print("🚀 Loading MakTek/Customer_support_faqs_dataset...")
    
    try:
        # Load the dataset
        dataset = load_dataset("MakTek/Customer_support_faqs_dataset")
        print(f"✅ Dataset loaded!")
        
        # Get the first split (usually 'train')
        split_name = list(dataset.keys())[0]
        data = dataset[split_name]
        
        print(f"📊 Processing {split_name} split with {len(data)} examples")
        print(f"📋 Available columns: {list(data[0].keys())}")
        
        # Extract FAQs - try common column names
        faqs = []
        for item in data:
            # Try different possible column combinations
            question = None
            answer = None
            
            # Common patterns for FAQ datasets
            if 'question' in item and 'answer' in item:
                question = item['question']
                answer = item['answer']
            elif 'input' in item and 'output' in item:
                question = item['input']
                answer = item['output']
            elif 'text' in item and 'label' in item:
                question = item['text']
                answer = item['label']
            elif len(item) >= 2:
                # Use first two columns
                keys = list(item.keys())
                question = item[keys[0]]
                answer = item[keys[1]]
            
            if question and answer:
                # Clean the text
                question = str(question).strip()
                answer = str(answer).strip()
                
                # Skip if too short
                if len(question) > 10 and len(answer) > 10:
                    faqs.append({
                        "question": question,
                        "answer": answer
                    })
        
        print(f"✅ Extracted {len(faqs)} valid FAQs")
        
        if not faqs:
            print("❌ No valid FAQs found. Check the dataset structure.")
            return
        
        # Show first few examples
        print("\n📝 Sample FAQs:")
        for i, faq in enumerate(faqs[:3]):
            print(f"{i+1}. Q: {faq['question'][:100]}...")
            print(f"   A: {faq['answer'][:100]}...")
            print()
        
        # Ingest to backend
        print("🔄 Ingesting to backend...")
        request_data = {"items": faqs}
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                "http://localhost:8000/api/ingest/faq",
                json=request_data
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"🎉 Successfully ingested {result['ingested']} FAQs!")
                print("✅ Your chatbot is now trained on the Hugging Face dataset!")
            else:
                print(f"❌ Error: {response.status_code} - {response.text}")
                
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n💡 Make sure:")
        print("1. Your backend server is running (python -m uvicorn app.main:app --reload --port 8000)")
        print("2. You have internet connection to download the dataset")
        print("3. You've installed the datasets library: pip install datasets")

if __name__ == "__main__":
    asyncio.run(ingest_hf_dataset())

