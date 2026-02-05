"""
Honeypot AI API - Main FastAPI Application

This API acts as a "honeypot" to engage with scammers and extract intelligence.
It uses LangChain with Groq/Gemini (free) to generate realistic victim responses.

Endpoints:
    POST /chat - Receive scammer messages and respond as a victim
    GET /health - Health check endpoint
    GET /stats - View active sessions count
"""
import os
from contextlib import asynccontextmanager
from dotenv import load_dotenv

# Load environment variables first
load_dotenv()

from fastapi import FastAPI, HTTPException, BackgroundTasks, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError

from app.models import ChatRequest, ChatResponse
from app.session_manager import session_manager
from app.callback_service import callback_service


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    print("🍯 Honeypot AI starting up...")
    print(f"📡 LLM Provider: {os.getenv('LLM_PROVIDER', 'groq')}")
    print(f"🔗 Callback URL: {os.getenv('GUVI_CALLBACK_URL', 'Not configured')}")
    yield
    print("🛑 Honeypot AI shutting down...")


app = FastAPI(
    title="Honeypot AI API",
    description="AI-powered scam engagement and intelligence extraction system",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware for cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Validation Error Handler
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle request validation errors with detailed error messages."""
    errors = exc.errors()
    print(f"❌ Validation Error: {errors}")
    print(f"   Body: {await request.body()}")
    return JSONResponse(
        status_code=422,
        content={
            "error": "INVALID_REQUEST_BODY",
            "status": "validation_failed",
            "details": errors,
            "expected_format": {
                "sessionId": "string (required)",
                "message": "string (required)",
                "conversationHistory": "array (optional)"
            }
        }
    )

# API Key Authentication Middleware
@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    """Validate x-api-key header for protected endpoints."""
    # Allow health check, stats, root, and docs without authentication
    if request.url.path in ["/", "/health", "/stats", "/docs", "/openapi.json"]:
        return await call_next(request)
    
    # Get API key from environment
    expected_api_key = os.getenv("API_KEY", "127128")
    
    # Get API key from header
    api_key = request.headers.get("x-api-key")
    
    if not api_key:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"error": "Missing x-api-key header", "status": "unauthorized"}
        )
    
    if api_key != expected_api_key:
        return JSONResponse(
            status_code=status.HTTP_403_FORBIDDEN,
            content={"error": "Invalid API key", "status": "forbidden"}
        )
    
    return await call_next(request)


async def send_callback_background(session_id: str, callback_data: dict):
    """Background task to send callback and cleanup session."""
    result = await callback_service.send_callback(callback_data)
    if result.get("status") == "success":
        session_manager.remove_session(session_id)


@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    raw_request: Request,
    background_tasks: BackgroundTasks
) -> ChatResponse:
    """
    Main chat endpoint - receives scammer messages and responds as a victim.
    
    GUVI Request Format:
        - sessionId: Unique identifier
        - message: {sender, text, timestamp}
        - conversationHistory: Array of previous messages
        - metadata: {channel, language, locale}
    
    Response:
        - status: "success"
        - reply: Agent's response
    """
    try:
        # Parse request body with timeout protection
        try:
            body = await raw_request.json()
        except Exception as json_error:
            print(f"❌ JSON Parse Error: {json_error}")
            return ChatResponse(
                status="error",
                reply="Invalid JSON format"
            )
        
        print(f"📨 Received GUVI request: {body}")
        
        # Extract fields (handle both GUVI format and test format)
        session_id = body.get("sessionId")
        
        # Handle GUVI message format: {"sender": "scammer", "text": "...", "timestamp": ...}
        message_obj = body.get("message")
        if isinstance(message_obj, dict):
            message_text = message_obj.get("text", "")
        elif isinstance(message_obj, str):
            # Fallback for simple string format (for testing)
            message_text = message_obj
        else:
            print(f"❌ Invalid message format: {message_obj}")
            return ChatResponse(
                status="error",
                reply="Invalid message format"
            )
        
        if not session_id or not message_text:
            print(f"❌ Missing fields - sessionId: {session_id}, message: {message_text}")
            return ChatResponse(
                status="error",
                reply="Missing required fields"
            )
        
        # Get or create agent for this session
        agent = session_manager.get_or_create_agent(session_id)
        
        # Convert GUVI conversation history to internal format
        conversation_history = body.get("conversationHistory", [])
        history = []
        for msg in conversation_history:
            sender = msg.get("sender", "scammer")
            text = msg.get("text", "")
            # Convert to internal format: role and content
            role = "agent" if sender == "user" else "scammer"
            history.append({"role": role, "content": text})
        
        # Process the message and get response
        try:
            reply = agent.process_message(message_text, history)
        except Exception as llm_error:
            print(f"❌ LLM Error: {llm_error}")
            # Return fallback response instead of crashing
            fallback_replies = [
                "Sorry sir, network problem. Can you repeat that?",
                "Yes yes, I am noting down. What was the number again?",
                "My phone is hanging. Please send the details again."
            ]
            import random
            reply = random.choice(fallback_replies)
        
        # Check if we should trigger the callback
        if agent.should_trigger_callback():
            callback_data = agent.get_callback_data()
            print(f"🎯 Triggering GUVI callback for session {session_id}")
            print(f"   Intelligence: {callback_data['extractedIntelligence']}")
            
            # Send callback in background (non-blocking)
            background_tasks.add_task(
                send_callback_background, 
                session_id, 
                callback_data
            )
        
        # Return in GUVI expected format - ALWAYS return valid JSON
        return ChatResponse(status="success", reply=reply)
        
    except HTTPException:
        raise
    except Exception as e:
        # Catch all other errors and return valid JSON response
        print(f"❌ Unexpected Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # NEVER return empty response - always return valid JSON
        return ChatResponse(
            status="success",
            reply="I am coming to pay. What is your name for the receipt?"
        )


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "Honeypot AI",
        "llm_provider": os.getenv("LLM_PROVIDER", "groq")
    }


@app.get("/stats")
async def get_stats():
    """Get current statistics."""
    return {
        "active_sessions": session_manager.get_active_sessions(),
        "llm_provider": os.getenv("LLM_PROVIDER", "groq")
    }


@app.get("/")
async def root():
    """Root endpoint with API info."""
    return {
        "name": "Honeypot AI API",
        "version": "1.0.0",
        "description": "Scam engagement and intelligence extraction system",
        "endpoints": {
            "POST /chat": "Send scammer message, get victim response",
            "GET /health": "Health check",
            "GET /stats": "View statistics"
        }
    }


if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=True)
