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

# API Key Authentication Middleware
@app.middleware("http")
async def api_key_middleware(request: Request, call_next):
    """Validate x-api-key header for protected endpoints."""
    # Allow health check and root without authentication
    if request.url.path in ["/", "/health", "/docs", "/openapi.json"]:
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
    request: ChatRequest, 
    background_tasks: BackgroundTasks
) -> ChatResponse:
    """
    Main chat endpoint - receives scammer messages and responds as a victim.
    
    Request Body:
        - sessionId: Unique identifier for this conversation
        - message: The scammer's current message
        - conversationHistory: List of previous messages (optional)
    
    Response:
        - status: "success" or "error"
        - reply: The honeypot agent's response
    
    Side Effects:
        - If enough intelligence is gathered, triggers a background callback to GUVI
    """
    try:
        # Get or create agent for this session
        agent = session_manager.get_or_create_agent(request.sessionId)
        
        # Convert history to dict format
        history = [
            {"role": msg.role, "content": msg.content}
            for msg in (request.conversationHistory or [])
        ]
        
        # Process the message and get response
        reply = agent.process_message(request.message, history)
        
        # Check if we should trigger the callback
        if agent.should_trigger_callback():
            callback_data = agent.get_callback_data()
            print(f"🎯 Triggering callback for session {request.sessionId}")
            print(f"   Intelligence: {callback_data['extractedIntelligence']}")
            
            # Send callback in background (non-blocking)
            background_tasks.add_task(
                send_callback_background, 
                request.sessionId, 
                callback_data
            )
        
        return ChatResponse(status="success", reply=reply)
        
    except Exception as e:
        print(f"❌ Error processing message: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Error processing message: {str(e)}"
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
