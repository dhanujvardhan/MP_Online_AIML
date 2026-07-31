"""
rag_engine.py
--------------
Core RAG (Retrieval-Augmented Generation) logic for the chatbot.

Pipeline:
1. Document is split into overlapping text chunks.
2. Each chunk is converted to a vector using a local SentenceTransformer model.
3. Vectors are stored in a FAISS index for fast similarity search.
4. On a user query, we embed the query, retrieve the top-k most similar chunks,
   build a prompt with that context, and ask a local (free, no API key) LLM
   to answer using only that context.

Everything here runs 100% locally -> no OpenAI/Anthropic key required.
Models are downloaded once from Hugging Face the first time you run the app
and are then cached locally by the `transformers` / `sentence-transformers` libraries.
"""

import os
import pickle
from typing import List, Dict

import numpy as np
import faiss
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
from transformers import pipeline

# ---------------------------------------------------------------------------
# Config
# ---------------------------------------------------------------------------
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"      # small, fast, free, local embedding model
LLM_MODEL_NAME = "google/flan-t5-base"          # small, free, local instruction-tuned LLM
CHUNK_SIZE = 500          # characters per chunk
CHUNK_OVERLAP = 80        # overlap between consecutive chunks
TOP_K = 3                 # number of chunks retrieved per query

DATA_DIR = os.path.join(os.path.dirname(__file__), "store")
INDEX_PATH = os.path.join(DATA_DIR, "faiss.index")
CHUNKS_PATH = os.path.join(DATA_DIR, "chunks.pkl")

os.makedirs(DATA_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# Text extraction
# ---------------------------------------------------------------------------
def extract_text(file_path: str) -> str:
    """Extract raw text from a .pdf or .txt file."""
    ext = os.path.splitext(file_path)[1].lower()

    if ext == ".pdf":
        reader = PdfReader(file_path)
        text = ""
        for page in reader.pages:
            page_text = page.extract_text() or ""
            text += page_text + "\n"
        return text

    elif ext == ".txt":
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            return f.read()

    else:
        raise ValueError(f"Unsupported file type: {ext}. Use .pdf or .txt")


# ---------------------------------------------------------------------------
# Chunking
# ---------------------------------------------------------------------------
def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """Split text into overlapping chunks so context isn't lost at boundaries."""
    text = " ".join(text.split())  # normalize whitespace
    if not text:
        return []

    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunks.append(text[start:end])
        start += chunk_size - overlap

    return [c.strip() for c in chunks if c.strip()]


# ---------------------------------------------------------------------------
# RAG Engine
# ---------------------------------------------------------------------------
class RAGEngine:
    def __init__(self):
        print("[RAGEngine] Loading embedding model (first run downloads it)...")
        self.embedder = SentenceTransformer(EMBEDDING_MODEL_NAME)
        self.embed_dim = self.embedder.get_sentence_embedding_dimension()

        print("[RAGEngine] Loading local LLM (first run downloads it)...")
        self.generator = pipeline("text2text-generation", model=LLM_MODEL_NAME)

        self.index = None
        self.chunks: List[Dict] = []  # {"text": str, "source": str}
        self._load_store()

    # --------------------------- persistence ---------------------------
    def _load_store(self):
        if os.path.exists(INDEX_PATH) and os.path.exists(CHUNKS_PATH):
            self.index = faiss.read_index(INDEX_PATH)
            with open(CHUNKS_PATH, "rb") as f:
                self.chunks = pickle.load(f)
            print(f"[RAGEngine] Loaded existing store with {len(self.chunks)} chunks.")
        else:
            self.index = faiss.IndexFlatL2(self.embed_dim)
            self.chunks = []

    def _save_store(self):
        faiss.write_index(self.index, INDEX_PATH)
        with open(CHUNKS_PATH, "wb") as f:
            pickle.dump(self.chunks, f)

    # --------------------------- ingestion ---------------------------
    def add_document(self, file_path: str, source_name: str) -> int:
        """Extract, chunk, embed and add a document to the vector store. Returns #chunks added."""
        text = extract_text(file_path)
        new_chunks = chunk_text(text)

        if not new_chunks:
            return 0

        embeddings = self.embedder.encode(new_chunks, show_progress_bar=False)
        embeddings = np.array(embeddings).astype("float32")

        self.index.add(embeddings)
        for c in new_chunks:
            self.chunks.append({"text": c, "source": source_name})

        self._save_store()
        return len(new_chunks)

    # --------------------------- retrieval ---------------------------
    def retrieve(self, query: str, top_k: int = TOP_K) -> List[Dict]:
        if self.index.ntotal == 0:
            return []

        query_vec = self.embedder.encode([query]).astype("float32")
        k = min(top_k, self.index.ntotal)
        distances, indices = self.index.search(query_vec, k)

        results = []
        for idx, dist in zip(indices[0], distances[0]):
            if idx == -1:
                continue
            results.append({**self.chunks[idx], "score": float(dist)})
        return results

    # --------------------------- generation ---------------------------
    def answer(self, query: str, top_k: int = TOP_K) -> Dict:
        retrieved = self.retrieve(query, top_k)

        if not retrieved:
            return {
                "answer": "Mujhe apne uploaded documents me is sawaal ka jawab nahi mila. "
                          "Pehle koi document upload karein ya sawaal rephrase karke try karein.",
                "sources": [],
            }

        context = "\n\n".join([f"- {r['text']}" for r in retrieved])
        prompt = (
            "Answer the question using ONLY the context below. "
            "If the answer is not in the context, say you don't know.\n\n"
            f"Context:\n{context}\n\n"
            f"Question: {query}\n"
            "Answer:"
        )

        result = self.generator(prompt, max_length=256, do_sample=False)
        answer_text = result[0]["generated_text"].strip()

        sources = list({r["source"] for r in retrieved})
        return {"answer": answer_text, "sources": sources}

    def reset(self):
        """Clear the entire knowledge base."""
        self.index = faiss.IndexFlatL2(self.embed_dim)
        self.chunks = []
        self._save_store()
