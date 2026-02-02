"""Test AI Assistant Module Backend

Tests the full stack: config → model loading → inference
"""

import sys
import os

# Add project root to path
sys.path.insert(0, os.path.abspath('.'))

from modules.ai_assistant.backend.config_service import ConfigService
from modules.ai_assistant.backend.llm_service import LLMService


def test_config():
    """Test configuration service"""
    print("\n1. Testing ConfigService...")
    config = ConfigService()
    
    model_path = config.get("model_path")
    print(f"   Model path: {model_path}")
    
    # Validate config
    is_valid, error = config.validate()
    if is_valid:
        print("   [OK] Configuration valid")
    else:
        print(f"   [ERROR] Configuration error: {error}")
        return False
    
    return True


def test_model_loading():
    """Test model loading"""
    print("\n2. Testing LLMService (Model Loading)...")
    print("   [NOTE] This will take 10-30 seconds (loading 1GB model into RAM)")
    
    config = ConfigService()
    llm_service = LLMService(config)
    
    # Load model
    success, error = llm_service.load_model()
    
    if success:
        print("   [OK] Model loaded successfully!")
        
        # Get model info
        info = llm_service.get_model_info()
        print(f"   Model size: {info['model_size_mb']} MB")
        print(f"   Model loaded: {info['loaded']}")
        
        return True
    else:
        print(f"   [ERROR] Model loading failed: {error}")
        return False


def test_inference():
    """Test simple inference"""
    print("\n3. Testing Inference (Text Generation)...")
    print("   [NOTE] This will take 5-10 seconds (generating response)")
    
    config = ConfigService()
    llm_service = LLMService(config)
    
    # Load model
    llm_service.load_model()
    
    # Simple test prompt
    prompt = "What is 2 + 2? Answer in one word:"
    
    print(f"   Prompt: {prompt}")
    result = llm_service.generate(prompt, max_tokens=10)
    
    if result["error"]:
        print(f"   [ERROR] Inference failed: {result['error']}")
        return False
    else:
        print(f"   Response: {result['text']}")
        print(f"   Tokens used: {result['tokens_used']}")
        print("   [OK] Inference works!")
        return True


if __name__ == "__main__":
    print("=" * 60)
    print("AI Assistant Backend Test")
    print("=" * 60)
    
    # Test each component
    tests = [
        ("Config", test_config),
        ("Model Loading", test_model_loading),
        ("Inference", test_inference)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            success = test_func()
            results.append((name, success))
        except Exception as e:
            print(f"\n[ERROR] {name} test crashed: {e}")
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for name, success in results:
        status = "[PASS]" if success else "[FAIL]"
        print(f"{status} - {name}")
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[SUCCESS] ALL TESTS PASSED! Backend is working!")
        sys.exit(0)
    else:
        print("\n[WARNING] Some tests failed. Check errors above.")
        sys.exit(1)
