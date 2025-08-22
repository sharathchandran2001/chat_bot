from fastapi import FastAPI
from pydantic import BaseModel
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics.pairwise import cosine_similarity
import json
import uuid
import numpy as np
from fastapi.middleware.cors import CORSMiddleware
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import threading
import os
import pickle
import hashlib

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
# File paths
# --------------------
KB_FILE = "kb.json"
INTENT_MODEL_FILE = "intent_model.pkl"
VECTORIZER_FILE = "vectorizer.pkl"
KB_VECTORIZER_FILE = "kb_vectorizer.pkl"
KB_EMBEDDINGS_FILE = "kb_embeddings.pkl"
KB_RESPONSES_FILE = "kb_responses.pkl"

# --------------------
# Session store
# --------------------
sessions = {}

# --------------------
# Helper: Hash KB for change detection
# --------------------
def file_hash(filepath):
    with open(filepath, "rb") as f:
        return hashlib.md5(f.read()).hexdigest()

last_kb_hash = None

# --------------------
# Load KB & Train or Load Models
# --------------------
def load_kb(force_reload=False):
    global df, clf, vectorizer, intent_responses
    global kb_vectorizer, kb_embeddings, kb_responses
    global last_kb_hash

    # Check KB file hash
    current_hash = file_hash(KB_FILE)
    if not force_reload and current_hash == last_kb_hash and os.path.exists(INTENT_MODEL_FILE):
        # Load existing models
        clf = pickle.load(open(INTENT_MODEL_FILE, "rb"))
        vectorizer = pickle.load(open(VECTORIZER_FILE, "rb"))
        intent_responses = pickle.load(open("intent_responses.pkl", "rb"))

        kb_vectorizer = pickle.load(open(KB_VECTORIZER_FILE, "rb"))
        kb_embeddings = pickle.load(open(KB_EMBEDDINGS_FILE, "rb"))
        kb_responses = pickle.load(open(KB_RESPONSES_FILE, "rb"))

        print("KB unchanged. Loaded models from disk.")
        return

    # Load KB
    with open(KB_FILE, "r", encoding="utf-8") as f:
        kb_data = json.load(f)
    df = kb_data

    # --------------------
    # Intent classifier
    # --------------------
    examples = [item['example'] for item in df]
    intents = [item['intent'] for item in df]

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(examples)

    clf = MultinomialNB()
    clf.fit(X, intents)

    intent_responses = {item['intent']: item['response'] for item in df}

    # Save models
    pickle.dump(clf, open(INTENT_MODEL_FILE, "wb"))
    pickle.dump(vectorizer, open(VECTORIZER_FILE, "wb"))
    pickle.dump(intent_responses, open("intent_responses.pkl", "wb"))

    # --------------------
    # Semantic embeddings
    # --------------------
    kb_vectorizer = TfidfVectorizer()
    kb_embeddings = kb_vectorizer.fit_transform(examples)
    kb_responses = [item['response'] for item in df]

    # Save semantic embeddings
    pickle.dump(kb_vectorizer, open(KB_VECTORIZER_FILE, "wb"))
    pickle.dump(kb_embeddings, open(KB_EMBEDDINGS_FILE, "wb"))
    pickle.dump(kb_responses, open(KB_RESPONSES_FILE, "wb"))

    last_kb_hash = current_hash
    print(f"KB loaded and models trained with {len(df)} entries.")

# Initial load
load_kb()

# --------------------
# KB Hot-Reload
# --------------------
class KBReloadHandler(FileSystemEventHandler):
    def on_modified(self, event):
        if event.src_path.endswith(KB_FILE):
            print("KB file changed. Reloading...")
            load_kb(force_reload=True)

observer = Observer()
observer.schedule(KBReloadHandler(), path=".", recursive=False)
observer.start()

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
# Shutdown observer
# --------------------
@app.on_event("shutdown")
def shutdown_event():
    observer.stop()
    observer.join()
