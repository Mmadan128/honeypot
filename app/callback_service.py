"""Callback Service - Sends final results to GUVI evaluation endpoint."""
import os
import httpx
from typing import Dict, Optional
import asyncio


class CallbackService:
    """Handles sending callback data to GUVI's evaluation endpoint."""
    
    def __init__(self):
        self.callback_url = os.getenv("GUVI_CALLBACK_URL", "")
        self.timeout = 30.0  # seconds
    
    async def send_callback(self, data: Dict) -> Dict:
        """
        Send the final callback to GUVI with extracted intelligence.
        
        Args:
            data: The callback payload containing sessionId, extractedIntelligence, etc.
            
        Returns:
            Response from GUVI's endpoint
        """
        if not self.callback_url:
            print("⚠️ GUVI_CALLBACK_URL not configured. Callback data:")
            print(data)
            return {"status": "skipped", "message": "No callback URL configured"}
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.post(
                    self.callback_url,
                    json=data,
                    headers={"Content-Type": "application/json"}
                )
                response.raise_for_status()
                
                print(f"✅ Callback sent successfully for session {data.get('sessionId')}")
                return {"status": "success", "response": response.json()}
                
        except httpx.TimeoutException:
            print(f"❌ Callback timeout for session {data.get('sessionId')}")
            return {"status": "error", "message": "Callback request timed out"}
            
        except httpx.HTTPStatusError as e:
            print(f"❌ Callback HTTP error: {e.response.status_code}")
            return {"status": "error", "message": f"HTTP {e.response.status_code}"}
            
        except Exception as e:
            print(f"❌ Callback failed: {str(e)}")
            return {"status": "error", "message": str(e)}
    
    def send_callback_sync(self, data: Dict) -> Dict:
        """Synchronous version of send_callback."""
        return asyncio.run(self.send_callback(data))


# Global callback service instance  
callback_service = CallbackService()
