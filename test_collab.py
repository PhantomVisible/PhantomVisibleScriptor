#!/usr/bin/env python3

print("Starting collaborative AI test...")

# Test basic imports
try:
    from utils.ollama_client import OllamaClient
    print("✅ OllamaClient imported")
except Exception as e:
    print(f"❌ OllamaClient import failed: {e}")

try:
    from agents.collaborative_agent import CollaborativeAgent
    print("✅ CollaborativeAgent imported")
except Exception as e:
    print(f"❌ CollaborativeAgent import failed: {e}")

# Test collaborative agent initialization
try:
    collab_agent = CollaborativeAgent(
        primary_model="llama3.1:8b",
        collaborator_model="mistral:latest"
    )
    print("✅ CollaborativeAgent initialized")
    
    # Test a simple collaborative review
    test_script = "This is a test script about Batman combat mechanics."
    test_topic = "Batman Arkham Knight combat"
    
    result = collab_agent.collaborative_review(test_script, test_topic)
    print("✅ Collaborative review completed")
    print(f"Models used: {result.get('models_used', [])}")
    
except Exception as e:
    print(f"❌ Collaborative test failed: {e}")
    import traceback
    traceback.print_exc()

print("Test completed!")
