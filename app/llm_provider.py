"""LLM Provider module - supports Groq and Google Gemini."""
import os
from typing import Optional
from langchain_core.language_models import BaseChatModel


def get_llm(provider: Optional[str] = None) -> BaseChatModel:
    """
    Get the LLM based on provider configuration.
    
    Args:
        provider: "groq" or "gemini". If None, reads from LLM_PROVIDER env var.
    
    Returns:
        Configured LLM instance
    """
    provider = provider or os.getenv("LLM_PROVIDER", "groq")
    
    if provider.lower() == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model="llama-3.3-70b-versatile",  # Latest model (updated Dec 2024)
            temperature=0.7,
            max_tokens=256,
            api_key=os.getenv("GROQ_API_KEY")
        )
    
    elif provider.lower() == "gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(
            model="gemini-1.5-flash",  # Fast and free
            temperature=0.7,
            max_output_tokens=256,
            google_api_key=os.getenv("GOOGLE_API_KEY")
        )
    
    else:
        raise ValueError(f"Unknown LLM provider: {provider}. Use 'groq' or 'gemini'")
