"""
Test script to verify GUVI endpoint compatibility.
This script tests various request formats that GUVI might send.
"""
import httpx
import json

# Update this to your deployed Render URL
API_URL = "https://honeypot-5jq3.onrender.com/chat"
API_KEY = "127128"

def test_endpoint():
    """Test the endpoint with different request formats."""
    
    test_cases = [
        {
            "name": "Minimal request (GUVI test format)",
            "data": {
                "sessionId": "test-session-001",
                "message": "Hello, test message"
            }
        },
        {
            "name": "With empty conversation history",
            "data": {
                "sessionId": "test-session-002",
                "message": "Urgent: Your bill is unpaid",
                "conversationHistory": []
            }
        },
        {
            "name": "With conversation history (dict format)",
            "data": {
                "sessionId": "test-session-003",
                "message": "Send payment to scammer@upi",
                "conversationHistory": [
                    {"role": "scammer", "content": "Your account is blocked"},
                    {"role": "agent", "content": "Oh no! What should I do?"}
                ]
            }
        },
        {
            "name": "Scam detection test",
            "data": {
                "sessionId": "test-session-004",
                "message": "Send 5000 INR to 9876543210 or we will disconnect your power"
            }
        }
    ]
    
    print("=" * 70)
    print("GUVI ENDPOINT COMPATIBILITY TEST")
    print("=" * 70)
    print(f"Testing: {API_URL}")
    print(f"API Key: {API_KEY}")
    print()
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n[Test {i}] {test['name']}")
        print(f"Request: {json.dumps(test['data'], indent=2)}")
        
        try:
            response = httpx.post(
                API_URL,
                json=test['data'],
                headers={
                    "x-api-key": API_KEY,
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            
            print(f"Status: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ SUCCESS")
                print(f"Response: {json.dumps(result, indent=2)}")
            else:
                print(f"❌ FAILED")
                print(f"Response: {response.text}")
                
        except httpx.TimeoutException:
            print(f"❌ TIMEOUT - Request took too long")
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
        
        print("-" * 70)
    
    print("\n" + "=" * 70)
    print("Test Complete!")
    print("=" * 70)


def test_authentication():
    """Test API key authentication."""
    print("\n" + "=" * 70)
    print("AUTHENTICATION TEST")
    print("=" * 70)
    
    # Test without API key
    print("\n[Test] No API Key")
    try:
        response = httpx.post(
            API_URL,
            json={"sessionId": "test", "message": "hi"},
            timeout=10.0
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        print("❌ Should have failed but didn't!")
    except Exception as e:
        print(f"✅ Correctly rejected: {e}")
    
    # Test with wrong API key
    print("\n[Test] Wrong API Key")
    try:
        response = httpx.post(
            API_URL,
            json={"sessionId": "test", "message": "hi"},
            headers={"x-api-key": "wrong-key"},
            timeout=10.0
        )
        print(f"Status: {response.status_code}")
        print(f"Response: {response.json()}")
        if response.status_code == 403:
            print("✅ Correctly rejected invalid key")
        else:
            print("❌ Should have returned 403")
    except Exception as e:
        print(f"Error: {e}")
    
    print("=" * 70)


if __name__ == "__main__":
    # First test authentication
    test_authentication()
    
    # Then test different request formats
    test_endpoint()
    
    print("\n📋 GUVI Configuration:")
    print(f"   URL: {API_URL}")
    print(f"   Header: x-api-key = {API_KEY}")
    print("\n✅ Your API is ready for GUVI testing!")
