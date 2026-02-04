"""LLM configuration and initialization."""
import os
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

def get_llm(temperature: float = 0.1) -> ChatGroq:
    """Initialize and return the Groq LLM instance."""
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is required")
    
    return ChatGroq(
        model="llama-3.3-70b-versatile",
        temperature=temperature,
        api_key=api_key
    )