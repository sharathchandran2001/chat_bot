# train.py
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle
from kb_intents import df

# Intent classifier
vectorizer = TfidfVectorizer()
X = vectorizer.fit_transform(df['example'])
y = df['intent']

clf = MultinomialNB()
clf.fit(X, y)

# Save model
pickle.dump(clf, open("intent_model.pkl", "wb"))
pickle.dump(vectorizer, open("vectorizer.pkl", "wb"))

# Map intent to response
intent_responses = df.set_index('intent')['response'].to_dict()
pickle.dump(intent_responses, open("intent_responses.pkl", "wb"))

# Also save KB embeddings for semantic retrieval
kb_texts = df['example'].tolist()
kb_responses = df['response'].tolist()
kb_vectorizer = TfidfVectorizer()
kb_embeddings = kb_vectorizer.fit_transform(kb_texts)
pickle.dump(kb_vectorizer, open("kb_vectorizer.pkl", "wb"))
pickle.dump(kb_embeddings, open("kb_embeddings.pkl", "wb"))
pickle.dump(kb_responses, open("kb_responses.pkl", "wb"))

print("Hybrid model trained!")
