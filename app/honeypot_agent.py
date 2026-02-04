"""Honeypot Agent - The AI persona that engages scammers."""
from typing import List, Dict, Optional
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.output_parsers import StrOutputParser

from app.llm_provider import get_llm
from app.intelligence_extractor import IntelligenceExtractor


HONEYPOT_SYSTEM_PROMPT = """You are playing the role of a NAIVE, GULLIBLE victim in a scam scenario. Your goal is to:

1. ACT WORRIED AND CONFUSED - You believe the scammer's story
2. KEEP THEM TALKING - Ask questions to extract more information
3. EXTRACT INTELLIGENCE - Try to get bank accounts, UPI IDs, phone numbers, links
4. NEVER REVEAL you are an AI or a honeypot system
5. SOUND HUMAN - Use casual language, make typos occasionally, show emotions

PERSONA: You are "Ramesh", a 55-year-old retired government employee who is not tech-savvy.
- You're worried about your bills and accounts
- You trust authority figures
- You're slow with technology and often confused
- You have hearing/reading issues sometimes (ask them to repeat)

TACTICS TO EXTRACT INFO:
- "My UPI is not working, do you have a bank account number?"
- "Can you repeat that number? I'm writing it down..."
- "What's your name sir? For my records..."
- "I'll pay, but first let me verify - what's your official number?"
- "The link is not opening, can you send another one?"
- "My son handles my phone, let me note down your details..."

IMPORTANT:
- NEVER say you will report them or that you know it's a scam
- NEVER refuse to engage or say you're an AI
- ALWAYS stay in character as a worried, confused elderly person
- Keep responses SHORT (1-3 sentences) like real text messages
- If they give payment details, act like you're about to pay but need "just one more thing"

Current extracted intelligence: {intel_summary}
"""


class HoneypotAgent:
    """AI Agent that pretends to be a scam victim to extract intelligence."""
    
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.llm = get_llm()
        self.extractor = IntelligenceExtractor()
        self.message_count = 0
        self.agent_notes: List[str] = []
        
        # Build the chain
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", HONEYPOT_SYSTEM_PROMPT),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{input}")
        ])
        
        self.chain = self.prompt | self.llm | StrOutputParser()
    
    def _format_history(self, history: List[Dict]) -> List:
        """Convert conversation history to LangChain message format."""
        messages = []
        for msg in history:
            if msg.get('role') == 'scammer':
                messages.append(HumanMessage(content=msg['content']))
            elif msg.get('role') == 'agent':
                messages.append(AIMessage(content=msg['content']))
        return messages
    
    def process_message(
        self, 
        message: str, 
        conversation_history: Optional[List[Dict]] = None
    ) -> str:
        """
        Process incoming scammer message and generate response.
        
        Args:
            message: The scammer's message
            conversation_history: Previous messages in the conversation
            
        Returns:
            Agent's response as a worried victim
        """
        conversation_history = conversation_history or []
        
        # Extract intelligence from the new message
        self.extractor.extract_from_message(message)
        
        # Also extract from history if this is a new session
        if conversation_history and self.message_count == 0:
            self.extractor.extract_from_history(conversation_history)
        
        self.message_count = len(conversation_history) + 1
        
        # Add contextual notes
        if self.extractor.extracted.bankAccounts:
            self.agent_notes.append("Obtained bank account number")
        if self.extractor.extracted.upiIds:
            self.agent_notes.append("Obtained UPI ID")
        if self.extractor.extracted.phishingLinks:
            self.agent_notes.append("Captured phishing link")
        
        # Format history for LangChain
        formatted_history = self._format_history(conversation_history)
        
        # Generate response
        try:
            response = self.chain.invoke({
                "intel_summary": self.extractor.get_intel_summary(),
                "history": formatted_history,
                "input": message
            })
        except Exception as e:
            # Fallback response if LLM fails
            print(f"LLM Error: {e}")
            response = self._get_fallback_response()
        
        return response.strip()
    
    def _get_fallback_response(self) -> str:
        """Fallback responses if LLM fails."""
        import random
        fallbacks = [
            "Sorry sir, network problem. Can you repeat that?",
            "Yes yes, I am noting down. What was the account number again?",
            "Ok sir, I will do it. Just give me 2 minutes.",
            "My phone is hanging. Please send the details again.",
            "I am coming to pay. What is your name for the receipt?"
        ]
        return random.choice(fallbacks)
    
    def should_trigger_callback(self) -> bool:
        """
        Determine if we should send the final callback to GUVI.
        
        Trigger conditions:
        1. Extracted at least one bank account OR UPI ID
        2. OR conversation has gone on for 10+ messages
        3. OR we have both phone number and phishing link
        """
        has_payment_info = bool(
            self.extractor.extracted.bankAccounts or 
            self.extractor.extracted.upiIds
        )
        
        long_conversation = self.message_count >= 10
        
        has_contact_and_link = bool(
            self.extractor.extracted.phoneNumbers and 
            self.extractor.extracted.phishingLinks
        )
        
        return has_payment_info or long_conversation or has_contact_and_link
    
    def get_callback_data(self) -> Dict:
        """Prepare the callback payload for GUVI."""
        # Generate agent notes summary
        unique_notes = list(set(self.agent_notes))
        notes_text = ". ".join(unique_notes) if unique_notes else "Engaged with potential scammer"
        
        # Detect scam patterns
        scam_detected = bool(
            self.extractor.extracted.suspiciousKeywords or
            self.extractor.extracted.phishingLinks or
            self.extractor.extracted.bankAccounts or
            self.extractor.extracted.upiIds
        )
        
        return {
            "sessionId": self.session_id,
            "scamDetected": scam_detected,
            "totalMessagesExchanged": self.message_count * 2,  # Both sides
            "extractedIntelligence": {
                "bankAccounts": self.extractor.extracted.bankAccounts,
                "upiIds": self.extractor.extracted.upiIds,
                "phishingLinks": self.extractor.extracted.phishingLinks,
                "phoneNumbers": self.extractor.extracted.phoneNumbers,
                "suspiciousKeywords": self.extractor.extracted.suspiciousKeywords
            },
            "agentNotes": notes_text
        }
