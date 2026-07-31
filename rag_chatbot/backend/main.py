"""
main.py
-------
FastAPI backend for the RAG Chatbot capstone project.

Endpoints:
  GET  /health          -> simple health check
  POST /upload           -> upload a .pdf or .txt file, it gets chunked + embedded + stored
  POST /chat              -> ask a question, get an answer grounded in uploaded documents
  POST /reset              -> clear the entire knowledge base
  GET  /status              -> how many chunks / documents are currently stored

Run with:
    uvicorn main:app --reload --port 8000
"""

import os
import shutil
import tempfile

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from rag_engine import RAGEngine

app = FastAPI(title="RAG Chatbot API", version="1.0.0")

# Allow the frontend (served from file:// or any localhost port) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load models once at startup (this can take a little while on first run
# since it downloads the models from Hugging Face and caches them locally).
print("Starting RAG engine... this may take a minute on first run.")
engine = RAGEngine()
print("RAG engine ready.")

ALLOWED_EXTENSIONS = {".pdf", ".txt"}


class ChatRequest(BaseModel):
    query: str
    top_k: int = 3


class ChatResponse(BaseModel):
    answer: str
    sources: list[str]


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/status")
def status():
    return {
        "total_chunks": len(engine.chunks),
        "documents": sorted(list({c["source"] for c in engine.chunks})),
    }


@app.post("/upload")
async def upload_document(file: UploadFile = File(...)):
    ext = os.path.splitext(file.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Only .pdf and .txt files are supported.")

    # Save to a temp file, process it, then discard the temp file
    with tempfile.NamedTemporaryFile(delete=False, suffix=ext) as tmp:
        shutil.copyfileobj(file.file, tmp)
        tmp_path = tmp.name

    try:
        num_chunks = engine.add_document(tmp_path, source_name=file.filename)
    finally:
        os.remove(tmp_path)

    if num_chunks == 0:
        raise HTTPException(status_code=400, detail="No extractable text found in this file.")

    return {
        "filename": file.filename,
        "chunks_added": num_chunks,
        "message": f"'{file.filename}' processed and added to the knowledge base.",
    }


@app.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    if not req.query.strip():
        raise HTTPException(status_code=400, detail="Query cannot be empty.")

    result = engine.answer(req.query, top_k=req.top_k)
    return ChatResponse(answer=result["answer"], sources=result["sources"])


@app.post("/reset")
def reset():
    engine.reset()
    return {"message": "Knowledge base cleared."}
