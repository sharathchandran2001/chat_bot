# kb.py
import pandas as pd

# Example -> Intent -> Response
data = [
    {"example": "hello", "intent": "greeting", "response": "Hello, how can I help you?"},
    {"example": "hi", "intent": "greeting", "response": "Hello, how can I help you?"},
    {"example": "who are you", "intent": "about_bot", "response": "I am MiniBot, your friendly AI assistant."},
    {"example": "what can you do", "intent": "capabilities", "response": "I can answer basic questions from my knowledge base."},
    {"example": "goodbye", "intent": "farewell", "response": "Goodbye and take care!"},
    {"example": "how are you", "intent": "greeting", "response": "I am just code, but I’m doing great if the server is running."},
    {"example": "what is your name", "intent": "about_bot", "response": "You can call me MiniBot."},
    {"example": "what is python", "intent": "tech_info", "response": "Python is a programming language used for AI, data science, and web apps."},
    {"example": "what is angular", "intent": "tech_info", "response": "Angular is a frontend framework for building single-page web applications."},
    {"example": "what is machine learning", "intent": "tech_info", "response": "Machine learning teaches computers to learn patterns from data."},
    {"example": "what is fastapi", "intent": "tech_info", "response": "FastAPI is a modern Python framework for building fast backend APIs."}
]

df = pd.DataFrame(data)
