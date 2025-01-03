import google.generativeai as genai
import os
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
import httpx

def get_gemini():

    llm = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash-exp",
        temperature=.5,
        max_tokens=None,
        timeout=None,
        max_retries=2,
        api_key=os.environ["GEMINI_API_KEY"]
    )

    return llm

def get_openai_compatible_model():
    llm = ChatOpenAI(
            model="llama-3.3-70b-versatile", 
            temperature=0.5,
            api_key=os.environ["GROQ_API_KEY"],
            base_url="https://api.groq.com/openai/v1/"
        )
    return llm


def get_ollama_model():
    api_key = os.environ["OLLAMA_API_KEY"]  # Ensure this environment variable is set
    base_url = "https://192.168.1.58/api"  # Your Ollama server base URL

    
    # Create the ChatOpenAI instance
    llm = ChatOpenAI(
        model="Gemma2:9b",
        temperature=0.5,
        base_url=base_url,
        http_client = httpx.Client(verify=False),
        api_key=api_key,       # Explicitly set the API key
    )
    return llm

def get_openrouter_model():
    api_key = os.environ["OPENROUTER_API_KEY"]  # Ensure this environment variable is set
    base_url = "https://openrouter.ai/api/v1"  # Your Ollama server base URL

    
    # Create the ChatOpenAI instance
    llm = ChatOpenAI(
        model="google/gemini-2.0-flash-exp:free",
        temperature=0,
        base_url=base_url,
        api_key=api_key,       # Explicitly set the API key
    )
    return llm