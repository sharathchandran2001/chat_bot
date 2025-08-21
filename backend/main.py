from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import uuid

app = FastAPI()

# --- Extended KB ---
knowledge_base = {
    "hello": "Hello, how can I help you?",
    "who are you": "I am a simple chatbot created to answer basic questions.",
    "what can you do": "I can provide simple answers from my knowledge base.",
    "goodbye": "Goodbye and take care!",
    "how are you": "I am just code, but I’m doing great if the server is running.",
    "what is your name": "You can call me MiniBot.",
    "what is python": "Python is a popular programming language used for AI, data science, and web apps.",
    "what is angular": "Angular is a frontend framework for building single-page web applications.",
    "what is machine learning": "Machine learning is teaching computers to learn patterns from data instead of being explicitly programmed.",
    "what is fastapi": "FastAPI is a modern Python framework for building fast backend APIs."
}

# Prepare vectorizer
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(knowledge_base.keys())

# --- Session store ---
sessions = {}

class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    if not request.session_id or request.session_id not in sessions:
        session_id = str(uuid.uuid4())
        sessions[session_id] = []
    else:
        session_id = request.session_id

    sessions[session_id].append(request.message)

    # Find best match
    query_vec = vectorizer.transform([request.message.lower()])
    sim = cosine_similarity(query_vec, X).flatten()
    idx = sim.argmax()
    matched_question = list(knowledge_base.keys())[idx]
    response = knowledge_base[matched_question]

    sessions[session_id].append(response)

    return {"session_id": session_id, "response": response}
