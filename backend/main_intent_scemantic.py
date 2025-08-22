from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.metrics.pairwise import cosine_similarity
import pickle
import uuid
import numpy as np
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load intent classifier
clf = pickle.load(open("intent_model.pkl", "rb"))
vectorizer = pickle.load(open("vectorizer.pkl", "rb"))
intent_responses = pickle.load(open("intent_responses.pkl", "rb"))

# Load KB embeddings for semantic retrieval
kb_vectorizer = pickle.load(open("kb_vectorizer.pkl", "rb"))
kb_embeddings = pickle.load(open("kb_embeddings.pkl", "rb"))
kb_responses = pickle.load(open("kb_responses.pkl", "rb"))

# Session store
sessions = {}

class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str

@app.post("/chat")
async def chat(request: ChatRequest):
    # Session
    if not request.session_id or request.session_id not in sessions:
        session_id = str(uuid.uuid4())
        sessions[session_id] = []
    else:
        session_id = request.session_id

    sessions[session_id].append(request.message)
    msg_lower = request.message.lower()

    # -----------------------------
    # Step 1: Intent classifier
    # -----------------------------
    X_test = vectorizer.transform([msg_lower])
    intent = clf.predict(X_test)[0]
    intent_response = intent_responses.get(intent, None)

    # -----------------------------
    # Step 2: Semantic retrieval
    # -----------------------------
    query_vec = kb_vectorizer.transform([msg_lower])
    sim_scores = cosine_similarity(query_vec, kb_embeddings).flatten()
    best_idx = np.argmax(sim_scores)
    semantic_response = kb_responses[best_idx]

    # -----------------------------
    # Combine: prefer intent if high confidence
    # -----------------------------
    # Here using NB confidence; fallback to semantic similarity
    probs = clf.predict_proba(X_test).max()
    if probs >= 0.4:   # threshold
        response = intent_response
    else:
        response = semantic_response

    sessions[session_id].append(response)
    return {"session_id": session_id, "response": response}
