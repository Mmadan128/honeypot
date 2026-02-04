"""Pydantic models for request/response handling."""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class Message(BaseModel):
    """Message structure from GUVI."""
    sender: str  # "scammer" or "user"
    text: str
    timestamp: int  # Epoch time in ms


class Metadata(BaseModel):
    """Optional metadata about the conversation."""
    channel: Optional[str] = "SMS"
    language: Optional[str] = "English"
    locale: Optional[str] = "IN"


class ConversationMessage(BaseModel):
    """Message in conversation history."""
    sender: str
    text: str
    timestamp: int


class ChatRequest(BaseModel):
    """Incoming request from GUVI's platform."""
    sessionId: str = Field(..., description="Unique session identifier")
    message: Message = Field(..., description="Current incoming message")
    conversationHistory: List[ConversationMessage] = Field(
        default_factory=list,
        description="Previous messages in this session"
    )
    metadata: Optional[Metadata] = Field(
        default=None,
        description="Optional metadata"
    )


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
