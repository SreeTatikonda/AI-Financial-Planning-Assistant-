"""
Chat API Routes
General conversational interface for financial questions
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import List, Optional
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


class Message(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    message: str
    conversation_history: Optional[List[Message]] = []


class ChatResponse(BaseModel):
    response: str
    sources: Optional[List[dict]] = None


@router.post("/", response_model=ChatResponse)
async def chat(
    data: ChatRequest,
    request: Request
):
    """
    General chat endpoint for financial questions
    Uses RAG to retrieve relevant financial knowledge
    """
    try:
        llm_service = request.app.state.llm_service
        vector_service = request.app.state.vector_service
        
        # Search for relevant financial knowledge
        search_results = vector_service.search_all_collections(
            query=data.message,
            n_results_per_collection=2
        )
        
        # Flatten results
        all_results = []
        for collection, results in search_results.items():
            all_results.extend(results)
        
        # Build context from retrieved knowledge
        context = "\n".join([
            f"- {result['text']}"
            for result in all_results[:5]  # Top 5 results
        ])
        
        # Build system prompt
        system_prompt = f"""You are a helpful financial planning assistant. You provide 
        personalized, actionable advice to help users improve their financial health.
        
        Use the following financial knowledge to inform your responses:
        {context}
        
        Be friendly, encouraging, and specific. If you don't have enough information
        to give accurate advice, ask clarifying questions.
        """
        
        # Build conversation history
        conversation = ""
        if data.conversation_history:
            for msg in data.conversation_history[-5:]:  # Last 5 messages
                conversation += f"{msg.role}: {msg.content}\n"
        
        # Generate response
        response = await llm_service.generate(
            prompt=f"{conversation}\nuser: {data.message}",
            system_prompt=system_prompt,
            temperature=0.7,
            max_tokens=500
        )
        
        # Prepare sources
        sources = [
            {
                "text": result["text"][:200] + "..." if len(result["text"]) > 200 else result["text"],
                "category": result["metadata"].get("category", "general")
            }
            for result in all_results[:3]
        ] if all_results else None
        
        logger.info(f"Chat response generated for: {data.message[:50]}...")
        
        return ChatResponse(
            response=response.strip(),
            sources=sources
        )
        
    except Exception as e:
        logger.error(f"Chat failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/knowledge-search")
async def search_knowledge(
    query: str,
    request: Request
):
    """
    Search financial knowledge base directly
    """
    try:
        vector_service = request.app.state.vector_service
        
        results = vector_service.search_all_collections(
            query=query,
            n_results_per_collection=3
        )
        
        return {
            "query": query,
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Knowledge search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))
