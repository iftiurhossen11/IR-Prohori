from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import sys
import os
import traceback

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.retrieve import retrieve
from src.hybrid import generate_hybrid_answer

app = FastAPI(title="IR Prohori API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class HistoryItem(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    role: str = "Student"
    chat_id: str = "default"
    history: Optional[List[HistoryItem]] = []
    memory: Optional[str] = ""

class ChatResponse(BaseModel):
    answer: str
    sources: list
    source_type: str

@app.get("/")
def root():
    return {"status": "IR Prohori API is running"}

@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        print("\n========== CHAT REQUEST ==========")
        print(f"Message: {request.message}")
        print(f"Memory: {request.memory}")
        print(f"History items: {len(request.history) if request.history else 0}")

        chunks = retrieve(request.message, k=4)
        print(f"Retrieved {len(chunks)} chunks")

        history = []
        if request.history:
            history = [{"role": h.role, "content": h.content} for h in request.history]

        result = generate_hybrid_answer(
            request.message,
            chunks,
            history=history,
            memory=request.memory or ""
        )

        print(f"Answer Type: {result.get('type')}")
        print(f"Answer Length: {len(result.get('answer', ''))}")
        print(f"Answer Preview: {result.get('answer', '')[:200]}")
        print("==================================\n")

        sources_list = []
        if result.get("type") == "verified":
            for i, c in enumerate(chunks, 1):
                source = c.metadata.get("source", "Unknown")
                source_name = os.path.basename(source)
                sources_list.append({
                    "id": i,
                    "name": source_name,
                    "snippet": c.page_content[:250] + "..."
                })

        return ChatResponse(
            answer=result.get("answer", ""),
            sources=sources_list,
            source_type=result.get("type", "general")
        )
    except Exception as e:
        print(f"ERROR: {str(e)}")
        traceback.print_exc()
        return ChatResponse(
            answer=f"Error: {str(e)}",
            sources=[],
            source_type="error"
        )