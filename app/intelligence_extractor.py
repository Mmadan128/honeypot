"""Intelligence extraction module - extracts scammer info using regex + LLM."""
import re
from typing import List, Tuple
from app.models import ExtractedIntelligence


class IntelligenceExtractor:
    """Extracts bank accounts, UPI IDs, phone numbers, links from text."""
    
    # Regex patterns for extraction
    PATTERNS = {
        # Indian bank account numbers (9-18 digits)
        'bank_account': r'\b\d{9,18}\b',
        
        # UPI IDs (username@bank format)
        'upi_id': r'\b[a-zA-Z0-9._-]+@[a-zA-Z]{2,}\b',
        
        # Phone numbers (Indian format)
        'phone': r'\b(?:\+91[-\s]?)?[6-9]\d{9}\b',
        
        # URLs and shortened links
        'links': r'(?:https?://)?(?:www\.)?(?:bit\.ly|tinyurl\.com|t\.co|goo\.gl|[a-zA-Z0-9-]+\.[a-zA-Z]{2,})(?:/[^\s]*)?',
        
        # IFSC codes
        'ifsc': r'\b[A-Z]{4}0[A-Z0-9]{6}\b',
    }
    
    # Suspicious keywords that indicate scam
    SUSPICIOUS_KEYWORDS = [
        'urgent', 'immediately', 'disconnection', 'blocked', 'suspended',
        'verify', 'confirm', 'expire', 'limited time', 'act now',
        'lottery', 'winner', 'prize', 'congratulations', 'selected',
        'kyc', 'update', 'link', 'click', 'pay now', 'transfer',
        'otp', 'pin', 'password', 'cvv', 'card number',
        'arrest', 'legal action', 'police', 'court', 'warrant',
        'refund', 'cashback', 'bonus', 'offer', 'free',
        'bank', 'rbi', 'government', 'ministry', 'official'
    ]
    
    def __init__(self):
        self.extracted = ExtractedIntelligence()
        self.all_messages: List[str] = []
    
    def extract_from_message(self, message: str) -> ExtractedIntelligence:
        """Extract intelligence from a single message."""
        message_lower = message.lower()
        self.all_messages.append(message)
        
        # Extract bank accounts
        bank_accounts = re.findall(self.PATTERNS['bank_account'], message)
        for acc in bank_accounts:
            if acc not in self.extracted.bankAccounts and len(acc) >= 10:
                self.extracted.bankAccounts.append(acc)
        
        # Extract UPI IDs (filter out email-like patterns)
        upi_ids = re.findall(self.PATTERNS['upi_id'], message)
        for upi in upi_ids:
            # Filter out common email domains
            if not any(domain in upi.lower() for domain in ['gmail', 'yahoo', 'hotmail', 'outlook']):
                if upi not in self.extracted.upiIds:
                    self.extracted.upiIds.append(upi)
        
        # Extract phone numbers
        phones = re.findall(self.PATTERNS['phone'], message)
        for phone in phones:
            clean_phone = re.sub(r'[\s-]', '', phone)
            if clean_phone not in self.extracted.phoneNumbers:
                self.extracted.phoneNumbers.append(clean_phone)
        
        # Extract links
        links = re.findall(self.PATTERNS['links'], message, re.IGNORECASE)
        for link in links:
            if link not in self.extracted.phishingLinks:
                self.extracted.phishingLinks.append(link)
        
        # Extract suspicious keywords
        for keyword in self.SUSPICIOUS_KEYWORDS:
            if keyword in message_lower and keyword not in [k.lower() for k in self.extracted.suspiciousKeywords]:
                self.extracted.suspiciousKeywords.append(keyword.capitalize())
        
        return self.extracted
    
    def extract_from_history(self, history: List[dict]) -> ExtractedIntelligence:
        """Extract intelligence from entire conversation history."""
        for msg in history:
            if msg.get('role') == 'scammer':
                self.extract_from_message(msg.get('content', ''))
        return self.extracted
    
    def has_valuable_intel(self) -> bool:
        """Check if we have extracted valuable intelligence."""
        return bool(
            self.extracted.bankAccounts or 
            self.extracted.upiIds or 
            (len(self.extracted.phoneNumbers) > 0 and len(self.extracted.phishingLinks) > 0)
        )
    
    def get_intel_summary(self) -> str:
        """Generate a summary of extracted intelligence."""
        parts = []
        if self.extracted.bankAccounts:
            parts.append(f"Bank Accounts: {', '.join(self.extracted.bankAccounts)}")
        if self.extracted.upiIds:
            parts.append(f"UPI IDs: {', '.join(self.extracted.upiIds)}")
        if self.extracted.phoneNumbers:
            parts.append(f"Phone Numbers: {', '.join(self.extracted.phoneNumbers)}")
        if self.extracted.phishingLinks:
            parts.append(f"Links: {', '.join(self.extracted.phishingLinks)}")
        return "; ".join(parts) if parts else "No intelligence extracted yet"
