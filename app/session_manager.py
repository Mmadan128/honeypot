"""Session Manager - Handles multiple concurrent scammer sessions."""
from typing import Dict, Optional
from datetime import datetime, timedelta
import threading

from app.honeypot_agent import HoneypotAgent


class SessionManager:
    """Manages honeypot agent sessions for multiple concurrent scammers."""
    
    def __init__(self, session_timeout_minutes: int = 30):
        self._sessions: Dict[str, Dict] = {}
        self._lock = threading.Lock()
        self._timeout = timedelta(minutes=session_timeout_minutes)
    
    def get_or_create_agent(self, session_id: str) -> HoneypotAgent:
        """
        Get existing agent for session or create new one.
        
        Args:
            session_id: Unique session identifier from GUVI
            
        Returns:
            HoneypotAgent instance for this session
        """
        with self._lock:
            # Clean up expired sessions
            self._cleanup_expired()
            
            if session_id not in self._sessions:
                self._sessions[session_id] = {
                    "agent": HoneypotAgent(session_id),
                    "created_at": datetime.now(),
                    "last_activity": datetime.now()
                }
            else:
                self._sessions[session_id]["last_activity"] = datetime.now()
            
            return self._sessions[session_id]["agent"]
    
    def remove_session(self, session_id: str) -> None:
        """Remove a session after callback is sent."""
        with self._lock:
            if session_id in self._sessions:
                del self._sessions[session_id]
    
    def _cleanup_expired(self) -> None:
        """Remove sessions that have been inactive for too long."""
        now = datetime.now()
        expired = [
            sid for sid, data in self._sessions.items()
            if now - data["last_activity"] > self._timeout
        ]
        for sid in expired:
            del self._sessions[sid]
    
    def get_active_sessions(self) -> int:
        """Return count of active sessions."""
        with self._lock:
            self._cleanup_expired()
            return len(self._sessions)


# Global session manager instance
session_manager = SessionManager()
