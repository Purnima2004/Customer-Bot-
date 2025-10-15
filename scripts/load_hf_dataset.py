#!/usr/bin/env python3
"""
Hugging Face Dataset Loader for AI Customer Support Bot
This script loads the MakTek/Customer_support_faqs_dataset and prepares it for ingestion
"""

import asyncio
import httpx
from datasets import load_dataset
from typing import List, Dict, Any
import json

class HFDatasetLoader:
    def __init__(self, dataset_name: str = "MakTek/Customer_support_faqs_dataset"):
        self.dataset_name = dataset_name
        self.dataset = None
        self.faqs = []
    
    def load_dataset(self):
        """Load the Hugging Face dataset"""
        print(f"🔄 Loading dataset: {self.dataset_name}")
        try:
            self.dataset = load_dataset(self.dataset_name)
            print(f"✅ Dataset loaded successfully!")
            print(f"📊 Dataset info:")
            print(f"   - Split: {list(self.dataset.keys())}")
            
        
            for split_name, split_data in self.dataset.items():
                print(f"   - {split_name}: {len(split_data)} examples")
                if len(split_data) > 0:
                    print(f"   - Sample columns: {list(split_data[0].keys())}")
                    print(f"   - First example: {split_data[0]}")
                break 
                
        except Exception as e:
            print(f"❌ Error loading dataset: {e}")
            return False
        return True
    
    def extract_faqs(self, split: str = "train") -> List[Dict[str, str]]:
        """Extract FAQs from the dataset in the format needed for our API"""
        if not self.dataset:
            print("❌ Dataset not loaded. Call load_dataset() first.")
            return []
        
        if split not in self.dataset:
            print(f"❌ Split '{split}' not found in dataset. Available splits: {list(self.dataset.keys())}")
            return []
        
        print(f"🔄 Extracting FAQs from '{split}' split...")
        
        # Getting the data
        data = self.dataset[split]
        faqs = []
        
       
        columns = list(data[0].keys())
        print(f"📋 Available columns: {columns}")
        
        
        question_cols = ['question', 'Question', 'query', 'Query', 'text', 'Text', 'input', 'Input']
        answer_cols = ['answer', 'Answer', 'response', 'Response', 'output', 'Output', 'target', 'Target']
        
        question_col = None
        answer_col = None
        
        # Finding question column
        for col in question_cols:
            if col in columns:
                question_col = col
                break
        
        # Finding answer column  
        for col in answer_cols:
            if col in columns:
                answer_col = col
                break
        
        if not question_col or not answer_col:
            print(f"❌ Could not identify question/answer columns.")
            print(f"   Looking for question in: {question_cols}")
            print(f"   Looking for answer in: {answer_cols}")
            print(f"   Available columns: {columns}")
            return []
        
        print(f"✅ Using columns: '{question_col}' -> '{answer_col}'")
        
        # Extracting FAQs
        for i, item in enumerate(data):
            try:
                question = str(item[question_col]).strip()
                answer = str(item[answer_col]).strip()
                
                # Skipping empty or very short entries
                if len(question) < 10 or len(answer) < 10:
                    continue
                
                faqs.append({
                    "question": question,
                    "answer": answer
                })
                
            except Exception as e:
                print(f"⚠️  Error processing item {i}: {e}")
                continue
        
        print(f"✅ Extracted {len(faqs)} FAQs")
        self.faqs = faqs
        return faqs
    
    def save_faqs_to_file(self, filename: str = "hf_faqs.json"):
        """Save extracted FAQs to a JSON file"""
        if not self.faqs:
            print("❌ No FAQs to save. Extract FAQs first.")
            return False
        
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.faqs, f, indent=2, ensure_ascii=False)
            print(f"✅ FAQs saved to {filename}")
            return True
        except Exception as e:
            print(f"❌ Error saving FAQs: {e}")
            return False
    
    async def ingest_to_backend(self, backend_url: str = "http://localhost:8000"):
        """Ingest the extracted FAQs to the backend API"""
        if not self.faqs:
            print("❌ No FAQs to ingest. Extract FAQs first.")
            return False
        
        print(f"🔄 Ingesting {len(self.faqs)} FAQs to backend...")
        
        # Preparing the request data
        request_data = {
            "items": self.faqs
        }
        
        try:
            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{backend_url}/api/ingest/faq",
                    json=request_data
                )
                
                if response.status_code == 200:
                    result = response.json()
                    print(f"✅ Successfully ingested {result['ingested']} FAQ items!")
                    return True
                else:
                    print(f"❌ Error: {response.status_code} - {response.text}")
                    return False
                    
        except httpx.ConnectError:
            print("❌ Error: Could not connect to the backend server.")
            print("Make sure your FastAPI server is running on http://localhost:8000")
            return False
        except Exception as e:
            print(f"❌ Error: {e}")
            return False

async def main():
    """Main function to load and process the dataset"""
    print("🚀 Hugging Face Dataset Loader for AI Customer Support Bot")
    print("=" * 60)
    
    
    loader = HFDatasetLoader()
    

    if not loader.load_dataset():
        return
    
   
    all_faqs = []
    for split_name in loader.dataset.keys():
        print(f"\n📂 Processing split: {split_name}")
        faqs = loader.extract_faqs(split_name)
        all_faqs.extend(faqs)
    
   
    seen_questions = set()
    unique_faqs = []
    for faq in all_faqs:
        if faq["question"] not in seen_questions:
            seen_questions.add(faq["question"])
            unique_faqs.append(faq)
    
    print(f"\n📊 Final dataset: {len(unique_faqs)} unique FAQs")
    loader.faqs = unique_faqs
    
    
    loader.save_faqs_to_file("customer_support_faqs.json")
    
  
    print(f"\n🤔 Do you want to ingest these FAQs to your backend? (y/n): ", end="")
    try:
        choice = input().lower().strip()
        if choice in ['y', 'yes']:
            await loader.ingest_to_backend()
        else:
            print("📁 FAQs saved to 'customer_support_faqs.json'. You can ingest them later.")
    except KeyboardInterrupt:
        print("\n👋 Exiting...")

if __name__ == "__main__":
    asyncio.run(main())
