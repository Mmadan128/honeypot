# GUVI Testing Instructions

## ⚠️ Important Note About Render Free Tier

**This API is hosted on Render's free tier, which spins down after 15 minutes of inactivity.**

### First Request After Sleep
- **Cold start time**: 30-60 seconds
- **GUVI testers**: Please allow up to 60 seconds timeout for the first request
- **Subsequent requests**: Will be fast (< 2 seconds)

### Wake Up the Service Before Testing
To ensure the service is awake before GUVI's automated testing:

```bash
# Wake up call (do this 30 seconds before testing)
curl https://honeypot-5jq3.onrender.com/health
```

## API Configuration

**Endpoint URL:**
```
https://honeypot-5jq3.onrender.com/chat
```

**Headers:**
```
x-api-key: 127128
Content-Type: application/json
```

## Test Request

```bash
curl -X POST https://honeypot-5jq3.onrender.com/chat \
  -H "Content-Type: application/json" \
  -H "x-api-key: 127128" \
  -d '{
    "sessionId": "test-123",
    "message": {
      "sender": "scammer",
      "text": "Your bank account will be blocked today. Verify immediately.",
      "timestamp": 1769776085000
    },
    "conversationHistory": [],
    "metadata": {
      "channel": "SMS",
      "language": "English",
      "locale": "IN"
    }
  }'
```

## Expected Response

```json
{
  "status": "success",
  "reply": "Oh no! I thought I paid it. Where do I send the money?"
}
```

## Features Implemented

✅ Scam intent detection via keyword analysis  
✅ AI Agent with human-like persona (Ramesh, 55-year-old)  
✅ Multi-turn conversation handling  
✅ Intelligence extraction (UPI IDs, bank accounts, links, phone numbers)  
✅ Final result callback to GUVI endpoint  
✅ API key authentication  
✅ Session management  

## Intelligence Callback

When sufficient intelligence is gathered, the system automatically sends results to:
```
https://hackathon.guvi.in/api/updateHoneyPotFinalResult
```

Callback payload format:
```json
{
  "sessionId": "abc123-session-id",
  "scamDetected": true,
  "totalMessagesExchanged": 6,
  "extractedIntelligence": {
    "bankAccounts": ["9988776655"],
    "upiIds": ["scammer@upi"],
    "phishingLinks": ["http://malicious-link.example"],
    "phoneNumbers": ["+919876543210"],
    "suspiciousKeywords": ["urgent", "verify now", "account blocked"]
  },
  "agentNotes": "Scammer used urgency tactics and payment redirection"
}
```

## Team Information

**Team Name:** Mirage  
**Member:** Madan M  
**Technology Stack:**
- Python 3.12
- FastAPI
- LangChain
- Groq (Llama 3.1 70B)
- Render (Deployment)

## Support

If you encounter timeout issues, please:
1. Try the request again (first request wakes up the service)
2. Allow 60 seconds timeout for cold starts
3. Verify the health endpoint is responding first

Thank you for testing!
