"""
Configuration settings for the Agentic AI Retail System
"""
import os
from dotenv import load_dotenv

load_dotenv()

# =============================================================================
# GROQ API CONFIGURATION
# =============================================================================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# Available Groq Models (Updated Dec 2025)
GROQ_MODELS = {
    "fast": "llama-3.1-8b-instant",      # Fast, good for simple tasks
    "balanced": "llama-3.3-70b-versatile", # Balanced performance
    "smart": "llama-3.3-70b-versatile",   # Latest, best quality
    "mixtral": "mixtral-8x7b-32768",      # Good for complex reasoning
}

# Default model for each agent type
AGENT_MODELS = {
    "orchestrator": "llama-3.3-70b-versatile",  # Smart routing decisions
    "recommendation": "llama-3.3-70b-versatile", # Product recommendations
    "inventory": "llama-3.1-8b-instant",         # Fast stock checks
    "payment": "llama-3.1-8b-instant",           # Fast payment processing
}

# =============================================================================
# SUPABASE CONFIGURATION
# =============================================================================
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")  # Use anon/public key for client
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")  # Optional: for admin ops

# =============================================================================
# DEEPGRAM CONFIGURATION (Voice STT/TTS)
# =============================================================================
DEEPGRAM_API_KEY = os.getenv("DEEPGRAM_API_KEY")

# STT Settings
DEEPGRAM_STT_MODEL = "nova-2"  # Best accuracy
DEEPGRAM_STT_LANGUAGE = "en"

# TTS Settings - Aura Voices
DEEPGRAM_TTS_VOICE = "aura-asteria-en"  # Warm, professional female
# Other options:
# "aura-luna-en" - Friendly, casual female
# "aura-stella-en" - Clear, articulate female
# "aura-orion-en" - Professional male
# "aura-arcas-en" - Friendly male

# =============================================================================
# APPLICATION SETTINGS
# =============================================================================
APP_NAME = "Agentic AI Retail System"
APP_VERSION = "1.0.0-mvp"
DEBUG = os.getenv("DEBUG", "true").lower() == "true"

# Session settings
SESSION_TIMEOUT_MINUTES = 30
MAX_CONVERSATION_HISTORY = 20

# =============================================================================
# SUPPORTED LANGUAGES
# =============================================================================
SUPPORTED_LANGUAGES = {
    "en": "English",
    "es": "Spanish",
    "fr": "French",
    "de": "German",
    "hi": "Hindi",
    "zh": "Chinese",
    "ar": "Arabic",
}

DEFAULT_LANGUAGE = "en"

# =============================================================================
# MOOD CATEGORIES
# =============================================================================
MOOD_CATEGORIES = {
    "happy": {"emoji": "😊", "priority": 1, "response_tone": "enthusiastic"},
    "neutral": {"emoji": "😐", "priority": 2, "response_tone": "professional"},
    "confused": {"emoji": "😕", "priority": 2, "response_tone": "helpful"},
    "frustrated": {"emoji": "😤", "priority": 3, "response_tone": "empathetic"},
    "angry": {"emoji": "😠", "priority": 4, "response_tone": "calm_supportive"},
}

# =============================================================================
# INTENT CATEGORIES (for routing)
# =============================================================================
INTENT_CATEGORIES = {
    "browse": "recommendation",
    "search": "recommendation", 
    "recommend": "recommendation",
    "stock": "inventory",
    "availability": "inventory",
    "check": "inventory",
    "buy": "payment",
    "purchase": "payment",
    "pay": "payment",
    "cart": "payment",
    "checkout": "payment",
}

# =============================================================================
# RETAIL SETTINGS
# =============================================================================
CURRENCY = "USD"
CURRENCY_SYMBOL = "$"
TAX_RATE = 0.08  # 8% tax

# Payment settings (mock for MVP)
PAYMENT_METHODS = ["credit_card", "debit_card", "paypal", "apple_pay"]
