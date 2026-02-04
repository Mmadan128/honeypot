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
            "name": "GUVI Format - First message (no history)",
            "data": {
                "sessionId": "test-session-001",
                "message": {
                    "sender": "scammer",
                    "text": "Your bank account will be blocked today. Verify immediately.",
                    "timestamp": 1770005528731
                },
                "conversationHistory": [],
                "metadata": {
                    "channel": "SMS",
                    "language": "English",
                    "locale": "IN"
                }
            }
        },
        {
            "name": "GUVI Format - Second message (with history)",
            "data": {
                "sessionId": "test-session-002",
                "message": {
                    "sender": "scammer",
                    "text": "Share your UPI ID to avoid account suspension.",
                    "timestamp": 1770005528731
                },
                "conversationHistory": [
                    {
                        "sender": "scammer",
                        "text": "Your bank account will be blocked today. Verify immediately.",
                        "timestamp": 1770005528731
                    },
                    {
                        "sender": "user",
                        "text": "Why will my account be blocked?",
                        "timestamp": 1770005528731
                    }
                ],
                "metadata": {
                    "channel": "SMS",
                    "language": "English",
                    "locale": "IN"
                }
            }
        },
        {
            "name": "GUVI Format - UPI scam",
            "data": {
                "sessionId": "test-session-003",
                "message": {
                    "sender": "scammer",
                    "text": "Send payment to scammer@upi immediately",
                    "timestamp": 1770005528731
                },
                "conversationHistory": [],
                "metadata": {
                    "channel": "WhatsApp",
                    "language": "English",
                    "locale": "IN"
                }
            }
        },
        {
            "name": "GUVI Format - Bank account scam",
            "data": {
                "sessionId": "test-session-004",
                "message": {
                    "sender": "scammer",
                    "text": "Send 5000 INR to account 9876543210 or we will disconnect your power",
                    "timestamp": 1770005528731
                },
                "conversationHistory": [],
                "metadata": {
                    "channel": "SMS",
                    "language": "English",
                    "locale": "IN"
                }
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
