#!/usr/bin/env python3

print("Starting debug test...")

try:
    from utils.ollama_client import OllamaClient
    print("✅ OllamaClient import successful")
    
    client = OllamaClient()
    print("✅ OllamaClient created")
    
    if client.test_connection():
        print("✅ Ollama connection successful")
    else:
        print("❌ Ollama connection failed")
        
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

print("Debug test completed")
