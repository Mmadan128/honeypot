"""
Test script to simulate GUVI's scammer bot interactions.
Run this after starting the server to test the honeypot.
"""
import httpx
import json
import time

BASE_URL = "http://localhost:8000"


def test_conversation():
    """Simulate a multi-turn scam conversation."""
    session_id = "test-session-001"
    conversation_history = []
    
    # Simulated scammer messages
    scammer_messages = [
        "Urgent: Your electricity bill is unpaid. Pay now at bit.ly/fake-pay or power will be cut in 1 hour.",
        "Send 2000 INR to scammer@upi immediately to avoid disconnection.",
        "Fine. Account: 9988776655, IFSC: SCAM0001234. Do it now.",
        "Why are you delaying? Pay immediately or face legal action!",
    ]
    
    print("=" * 60)
    print("🧪 HONEYPOT API TEST - Simulating Scammer Conversation")
    print("=" * 60)
    
    for i, scammer_msg in enumerate(scammer_messages, 1):
        print(f"\n--- Turn {i} ---")
        print(f"🔴 Scammer: {scammer_msg}")
        
        # Send request to API
        payload = {
            "sessionId": session_id,
            "message": scammer_msg,
            "conversationHistory": conversation_history
        }
        
        try:
            response = httpx.post(
                f"{BASE_URL}/chat",
                json=payload,
                timeout=30.0
            )
            response.raise_for_status()
            result = response.json()
            
            print(f"🟢 Agent: {result['reply']}")
            
            # Update conversation history
            conversation_history.append({"role": "scammer", "content": scammer_msg})
            conversation_history.append({"role": "agent", "content": result['reply']})
            
        except httpx.RequestError as e:
            print(f"❌ Request failed: {e}")
            break
        except httpx.HTTPStatusError as e:
            print(f"❌ HTTP error: {e.response.status_code}")
            break
        
        # Small delay between messages
        time.sleep(1)
    
    print("\n" + "=" * 60)
    print("✅ Test completed!")
    print("=" * 60)


def test_health():
    """Test health endpoint."""
    try:
        response = httpx.get(f"{BASE_URL}/health")
        print(f"Health check: {response.json()}")
    except Exception as e:
        print(f"Health check failed: {e}")


def test_stats():
    """Test stats endpoint."""
    try:
        response = httpx.get(f"{BASE_URL}/stats")
        print(f"Stats: {response.json()}")
    except Exception as e:
        print(f"Stats failed: {e}")


if __name__ == "__main__":
    print("\n🔍 Checking API health...")
    test_health()
    
    print("\n📊 Checking stats...")
    test_stats()
    
    print("\n🎭 Starting conversation test...")
    test_conversation()
    
    print("\n📊 Final stats...")
    test_stats()
