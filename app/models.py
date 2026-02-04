"""Pydantic models for request/response handling."""
from pydantic import BaseModel
from typing import List, Optional, Dict, Any


class ConversationMessage(BaseModel):
    """Single message in conversation history."""
    role: str  # "scammer" or "agent"
    content: str


class ChatRequest(BaseModel):
    """Incoming request from GUVI's scammer bot."""
    sessionId: str
    message: str
    conversationHistory: Optional[List[ConversationMessage]] = []


class ChatResponse(BaseModel):
    """Response sent back to GUVI."""
    status: str
    reply: str


class ExtractedIntelligence(BaseModel):
    """Intelligence extracted from conversation."""
    bankAccounts: List[str] = []
    upiIds: List[str] = []
    phishingLinks: List[str] = []
    phoneNumbers: List[str] = []
    suspiciousKeywords: List[str] = []


class CallbackPayload(BaseModel):
    """Final callback payload sent to GUVI for evaluation."""
    sessionId: str
    scamDetected: bool
    totalMessagesExchanged: int
    extractedIntelligence: ExtractedIntelligence
    agentNotes: str
