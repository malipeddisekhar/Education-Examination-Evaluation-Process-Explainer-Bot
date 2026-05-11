#!/usr/bin/env python3
"""
Deployment Verification Script
Tests all critical components before deployment
"""

import os
import sys
from pathlib import Path

def test_imports():
    """Test all required imports"""
    print("🔍 Testing imports...")
    try:
        import streamlit
        print(f"  ✅ streamlit {streamlit.__version__}")
        
        import groq
        print(f"  ✅ groq {groq.__version__}")
        
        from langchain_huggingface import HuggingFaceEmbeddings
        print("  ✅ langchain_huggingface")
        
        from langchain_community.vectorstores import FAISS
        print("  ✅ FAISS")
        
        from PyPDF2 import PdfReader
        print("  ✅ PyPDF2")
        
        import speech_recognition
        print("  ✅ SpeechRecognition")
        
        from gtts import gTTS
        print("  ✅ gTTS")
        
        try:
            from pdf2image import convert_from_bytes
            import pytesseract
            print("  ✅ OCR support (pdf2image + pytesseract)")
        except ImportError:
            print("  ⚠️  OCR support not available (optional)")
        
        return True
    except ImportError as e:
        print(f"  ❌ Import failed: {e}")
        return False

def test_environment():
    """Test environment variables"""
    print("\n🔍 Testing environment variables...")
    
    api_key = os.getenv("GROQ_API_KEY")
    if api_key and api_key != "your_groq_api_key_here":
        print("  ✅ GROQ_API_KEY is set")
        return True
    else:
        print("  ❌ GROQ_API_KEY not set or invalid")
        print("     Set it in .env file or environment variables")
        return False

def test_files():
    """Test required files exist"""
    print("\n🔍 Testing required files...")
    
    required_files = [
        "app.py",
        "htmlTemplates.py",
        "requirements.txt",
        "Procfile",
        "render.yaml",
        "runtime.txt",
        "Aptfile",
        ".env.example",
        ".streamlit/config.toml"
    ]
    
    all_exist = True
    for file in required_files:
        if Path(file).exists():
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} missing")
            all_exist = False
    
    return all_exist

def test_requirements():
    """Test requirements.txt is valid"""
    print("\n🔍 Testing requirements.txt...")
    
    try:
        with open("requirements.txt", "r") as f:
            content = f.read()
            
        # Check for critical packages
        critical = [
            "streamlit",
            "groq",
            "langchain",
            "faiss-cpu",
            "transformers",
            "PyPDF2"
        ]
        
        all_found = True
        for package in critical:
            if package in content:
                print(f"  ✅ {package} found")
            else:
                print(f"  ❌ {package} missing")
                all_found = False
        
        # Check streamlit version
        if "streamlit==1.40" in content or "streamlit>=1.40" in content:
            print("  ✅ Streamlit version is correct")
        else:
            print("  ⚠️  Streamlit version may be incorrect")
        
        return all_found
    except Exception as e:
        print(f"  ❌ Error reading requirements.txt: {e}")
        return False

def test_app_syntax():
    """Test app.py has no syntax errors"""
    print("\n🔍 Testing app.py syntax...")
    
    try:
        with open("app.py", "r", encoding="utf-8") as f:
            code = f.read()
        
        compile(code, "app.py", "exec")
        print("  ✅ No syntax errors")
        return True
    except SyntaxError as e:
        print(f"  ❌ Syntax error: {e}")
        return False
    except Exception as e:
        print(f"  ❌ Error: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🚀 DEPLOYMENT VERIFICATION TEST")
    print("=" * 60)
    
    results = {
        "Imports": test_imports(),
        "Environment": test_environment(),
        "Files": test_files(),
        "Requirements": test_requirements(),
        "Syntax": test_app_syntax()
    }
    
    print("\n" + "=" * 60)
    print("📊 TEST RESULTS")
    print("=" * 60)
    
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20s} {status}")
    
    all_passed = all(results.values())
    
    print("\n" + "=" * 60)
    if all_passed:
        print("🎉 ALL TESTS PASSED - READY FOR DEPLOYMENT!")
    else:
        print("⚠️  SOME TESTS FAILED - FIX ISSUES BEFORE DEPLOYING")
    print("=" * 60)
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
