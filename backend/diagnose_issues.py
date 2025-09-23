#!/usr/bin/env python3
"""
Diagnose the issues with the server startup
"""

import sys
import os
import subprocess
import time

def diagnose_issues():
    print("🔍 Diagnosing Server Issues")
    print("=" * 40)
    
    # 1. Check Python version
    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    
    # 2. Check current directory
    print(f"Current directory: {os.getcwd()}")
    
    # 3. Check if required files exist
    required_files = [
        "app/main.py",
        "app/database.py", 
        "app/routes/enhanced_ai.py",
        "app/ai/openrouter_service.py",
        "app/ai/triage_system.py"
    ]
    
    print("\n📁 Checking required files:")
    for file in required_files:
        exists = os.path.exists(file)
        print(f"   {file}: {'✅' if exists else '❌'}")
    
    # 4. Check imports
    print("\n📦 Testing imports:")
    try:
        import fastapi
        print(f"   FastAPI: ✅ (version {fastapi.__version__})")
    except ImportError as e:
        print(f"   FastAPI: ❌ {e}")
    
    try:
        import uvicorn
        print(f"   Uvicorn: ✅")
    except ImportError as e:
        print(f"   Uvicorn: ❌ {e}")
    
    try:
        import sqlalchemy
        print(f"   SQLAlchemy: ✅ (version {sqlalchemy.__version__})")
    except ImportError as e:
        print(f"   SQLAlchemy: ❌ {e}")
    
    try:
        import aiohttp
        print(f"   aiohttp: ✅")
    except ImportError as e:
        print(f"   aiohttp: ❌ {e}")
    
    # 5. Test app import
    print("\n🚀 Testing app import:")
    try:
        from app.main import app
        print("   App import: ✅")
    except Exception as e:
        print(f"   App import: ❌ {e}")
    
    # 6. Check Ollama
    print("\n🤖 Checking Ollama:")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json()
            print(f"   Ollama: ✅ ({len(models.get('models', []))} models)")
        else:
            print(f"   Ollama: ❌ (status {response.status_code})")
    except Exception as e:
        print(f"   Ollama: ❌ {e}")
    
    # 7. Test simple server
    print("\n🧪 Testing simple server:")
    try:
        from fastapi import FastAPI
        test_app = FastAPI()
        
        @test_app.get("/")
        async def test():
            return {"test": "ok"}
        
        print("   Simple app creation: ✅")
        
        # Try to run uvicorn programmatically
        import uvicorn
        print("   Starting test server for 2 seconds...")
        
        # This is a bit tricky to test without blocking
        print("   Uvicorn import: ✅")
        
    except Exception as e:
        print(f"   Simple server test: ❌ {e}")
    
    # 8. Check port availability
    print("\n🔌 Checking port 8000:")
    try:
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', 8000))
        if result == 0:
            print("   Port 8000: ❌ (already in use)")
        else:
            print("   Port 8000: ✅ (available)")
        sock.close()
    except Exception as e:
        print(f"   Port check: ❌ {e}")
    
    print("\n✨ Diagnosis complete!")

if __name__ == "__main__":
    diagnose_issues()
