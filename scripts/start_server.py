#!/usr/bin/env python3
"""
Startup script for AI Customer Support Bot
This script checks dependencies and starts the server
"""

import os
import sys
import subprocess
import asyncio
from pathlib import Path

def check_env_file():
    """Check if .env file exists and has required keys"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found!")
        print("\nPlease create a .env file with your API keys:")
        print("GEMINI_API_KEY=AIzaSyC9XzFRsgoHn--WKlhyxxF-TPEd_YzQBeA")
        print("PINECONE_API_KEY=pcsk_5C61P8_DnhWY9sm59t2JnAd9F4rah5u9FNTGWSypYKv8nza3WrQVd1k5h3cUWX4mrczLH3")
        return False
    
    with open(env_file, 'r') as f:
        content = f.read()
        
    if "your_gemini_api_key_here" in content or "your_pinecone_api_key_here" in content:
        print("❌ Please replace the placeholder API keys in .env file with your actual keys!")
        return False
    
    print("✅ .env file found and configured")
    return True

def test_imports():
    """Test if all required modules can be imported"""
    try:
        from sentence_transformers import SentenceTransformer
        print("✅ sentence-transformers imported successfully")
    except ImportError as e:
        print(f"❌ sentence-transformers import failed: {e}")
        print("Run: python fix_dependencies.py")
        return False
    
    try:
        import google.generativeai as genai
        print("✅ google-generativeai imported successfully")
    except ImportError as e:
        print(f"❌ google-generativeai import failed: {e}")
        return False
    
    try:
        from pinecone import Pinecone
        print("✅ pinecone imported successfully")
    except ImportError as e:
        print(f"❌ pinecone import failed: {e}")
        return False
    
    return True

def create_env_example():
    """Create .env.example file if it doesn't exist"""
    env_example = Path(".env.example")
    if not env_example.exists():
        with open(env_example, 'w') as f:
            f.write("""# AI Customer Support Bot Environment Variables

# API Keys (Replace with your actual keys)
GEMINI_API_KEY=your_gemini_api_key_here
PINECONE_API_KEY=your_pinecone_api_key_here

# Database
DB_URL=sqlite+aiosqlite:///./data/app.db

# Models
CHAT_MODEL=models/gemini-2.0-flash-exp
EMBEDDING_MODEL=intfloat/e5-base-v2

# Pinecone
PINECONE_INDEX=ai-customer-bot-faq

# RAG Parameters
TOP_K=5
SCORE_THRESHOLD=0.75
MAX_CONTEXT_CHARS=2000

# Server
PORT=8000
ENV=development
LOG_LEVEL=INFO
""")
        print("✅ Created .env.example file")

def main():
    print("🚀 AI Customer Support Bot - Startup Check")
    print("=" * 50)
    
   
    if not Path("app/main.py").exists():
        print("❌ Please run this script from the project root directory")
        return
   
    create_env_example()
    

    if not check_env_file():
        return
    

    if not test_imports():
        return
    
    print("\n🎉 All checks passed! Starting server...")
    print("=" * 50)

    try:
        subprocess.run([
            sys.executable, "-m", "uvicorn", 
            "app.main:app", 
            "--reload", 
            "--host", "0.0.0.0", 
            "--port", "8000"
        ])
    except KeyboardInterrupt:
        print("\n👋 Server stopped by user")
    except Exception as e:
        print(f"❌ Failed to start server: {e}")

if __name__ == "__main__":
    main()
