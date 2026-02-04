# 🍯 Honeypot AI - Scam Detection & Intelligence Extraction

A LangChain-powered API that acts as a "honeypot" to engage with scammers and extract valuable intelligence (bank accounts, UPI IDs, phone numbers, phishing links).

## 🎯 Features

- **AI Persona**: Plays a naive, elderly victim to keep scammers engaged
- **Intelligence Extraction**: Automatically extracts bank accounts, UPI IDs, links, phone numbers
- **Session Management**: Handles multiple concurrent scammer conversations
- **Auto Callback**: Triggers GUVI evaluation when enough intelligence is gathered
- **Free LLMs**: Uses Groq (Llama 3.1) or Google Gemini - both free!

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install packages
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add your API key
# Get FREE Groq key: https://console.groq.com/keys
# Get FREE Gemini key: https://makersuite.google.com/app/apikey
```

### 3. Run the Server

```bash
# Development
python main.py

# Or with uvicorn directly
uvicorn main:app --reload --port 8000
```

### 4. Test the API

```bash
# In another terminal
python test_api.py
```

## 📡 API Endpoints

### POST /chat
Main endpoint for receiving scammer messages.

**Request:**
```json
{
  "sessionId": "unique-session-id",
  "message": "Your bill is unpaid. Pay at bit.ly/scam",
  "conversationHistory": [
    {"role": "scammer", "content": "Previous message"},
    {"role": "agent", "content": "Previous response"}
  ]
}
```

**Response:**
```json
{
  "status": "success",
  "reply": "Oh no! I thought I paid. Where do I send the money?"
}
```

### GET /health
Health check endpoint.

### GET /stats
View active session count.

## 🔑 Getting Free API Keys

### Groq (Recommended - Fastest)
1. Go to https://console.groq.com/keys
2. Sign up with Google/GitHub
3. Create an API key
4. Add to `.env`: `GROQ_API_KEY=your_key`

### Google Gemini
1. Go to https://makersuite.google.com/app/apikey
2. Sign in with Google
3. Create an API key
4. Add to `.env`: `GOOGLE_API_KEY=your_key`

## 🌐 Deploying to Render (Free)

1. Push code to GitHub
2. Go to https://render.com
3. Create new Web Service
4. Connect your GitHub repo
5. Add environment variables:
   - `GROQ_API_KEY` or `GOOGLE_API_KEY`
   - `LLM_PROVIDER` = `groq` or `gemini`
   - `GUVI_CALLBACK_URL` = Your GUVI evaluation URL
6. Deploy!

## 📋 GUVI Callback Format

When the agent extracts enough intelligence, it automatically sends:

```json
{
  "sessionId": "wertyu-dfghj-ertyui",
  "scamDetected": true,
  "totalMessagesExchanged": 6,
  "extractedIntelligence": {
    "bankAccounts": ["9988776655"],
    "upiIds": ["scammer@upi"],
    "phishingLinks": ["bit.ly/fake-pay"],
    "phoneNumbers": [],
    "suspiciousKeywords": ["Urgent", "disconnection"]
  },
  "agentNotes": "Obtained bank account number. Obtained UPI ID."
}
```

## 🛠️ Project Structure

```
honeypot/
├── main.py                    # FastAPI application
├── app/
│   ├── models.py              # Pydantic models
│   ├── llm_provider.py        # Groq/Gemini LLM setup
│   ├── honeypot_agent.py      # AI agent with persona
│   ├── intelligence_extractor.py  # Regex extraction
│   ├── session_manager.py     # Multi-session handling
│   └── callback_service.py    # GUVI callback sender
├── test_api.py                # Test script
├── requirements.txt           # Dependencies
├── .env.example               # Environment template
├── Procfile                   # Heroku/Render deployment
└── render.yaml                # Render.com config
```

## 🎭 How the AI Persona Works

The agent plays "Ramesh", a 55-year-old retired government employee who:
- Is worried about bills and accounts
- Trusts authority figures
- Is slow with technology
- Asks for details to be repeated
- Tries to get bank account/UPI info by saying "UPI not working"

## ⚙️ Customization

### Change the Persona
Edit the `HONEYPOT_SYSTEM_PROMPT` in `app/honeypot_agent.py`

### Adjust Callback Triggers
Edit `should_trigger_callback()` in `app/honeypot_agent.py`:
- Default: Triggers when bank account OR UPI ID is found
- Or after 10+ messages
- Or when phone + phishing link are found

### Add More Extraction Patterns
Edit `PATTERNS` dict in `app/intelligence_extractor.py`

## 📝 License

MIT License - Feel free to use and modify!
