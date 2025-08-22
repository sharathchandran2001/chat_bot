from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics.pairwise import cosine_similarity
import json
import uuid
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
import os
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading

# --------------------
# FastAPI Setup
# --------------------
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --------------------
# KB Reload Handler
# --------------------
KB_FILE = "kb.json"

class KBReloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(KB_FILE):
            print("KB file changed, reloading...")
            load_kb()

# Watcher thread
observer = Observer()
observer.schedule(KBReloadHandler(), path=".", recursive=False)
observer.start()

# --------------------
# Session store
# --------------------
sessions = {}

# --------------------
# Load KB & Train Models
# --------------------
def load_kb():
    global df, clf, vectorizer, intent_responses
    global kb_vectorizer, kb_embeddings, kb_responses

    with open(KB_FILE, "r", encoding="utf-8") as f:
        kb_data = json.load(f)

    # Convert JSON to list of dicts
    df = kb_data

    # Intent classifier
    examples = [item['example'] for item in df]
    intents = [item['intent'] for item in df]
    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(examples)
    clf = MultinomialNB()
    clf.fit(X, intents)
    intent_responses = {item['intent']: item['response'] for item in df}

    # Semantic embeddings
    kb_vectorizer = TfidfVectorizer()
    kb_embeddings = kb_vectorizer.fit_transform(examples)
    kb_responses = [item['response'] for item in df]

    print("KB loaded and models trained with", len(df), "entries.")

# Initial load
load_kb()

# --------------------
# Chat Request Model
# --------------------
class ChatRequest(BaseModel):
    session_id: str | None = None
    message: str

# --------------------
# Chat Endpoint
# --------------------
@app.post("/chat")
async def chat(request: ChatRequest):
    # Session
    if not request.session_id or request.session_id not in sessions:
        session_id = str(uuid.uuid4())
        sessions[session_id] = []
    else:
        session_id = request.session_id

    msg_lower = request.message.lower()
    sessions[session_id].append(request.message)

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
    # Hybrid logic
    # -----------------------------
    probs = clf.predict_proba(X_test).max()
    if probs >= 0.4:
        response = intent_response
    else:
        response = semantic_response

    sessions[session_id].append(response)
    return {"session_id": session_id, "response": response}

# --------------------
# Stop observer on shutdown
# --------------------
@app.on_event("shutdown")
def shutdown_event():
    observer.stop()
    observer.join()
