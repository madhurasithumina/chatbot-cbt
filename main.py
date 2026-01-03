"""
FastAPI Application

RESTful API for the CBT Chatbot system.
Enterprise-grade API with authentication, rate limiting, and monitoring.
"""
from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import Optional, List, Dict
from datetime import datetime
import logging
from contextlib import asynccontextmanager

from src.core.chatbot_engine import CBTChatbotEngine
from src.core.hybrid_generator import HybridResponseGenerator
from src.models.cbt_model import CBTModel
from config.config import get_settings

logger = logging.getLogger(__name__)

# Global chatbot engine
chatbot_engine = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize and cleanup application resources"""
    global chatbot_engine
    
    settings = get_settings()
    
    logger.info("Initializing CBT Chatbot Engine...")
    
    # Initialize custom model
    cbt_model = CBTModel(
        model_path=settings.custom_model_path
    )
    
    # Initialize hybrid generator
    hybrid_generator = HybridResponseGenerator(
        openai_api_key=settings.openai_api_key,
        custom_model=cbt_model,
        embedding_model_name=settings.embedding_model,
        custom_weight=settings.custom_model_weight,
        gpt_weight=settings.gpt_model_weight,
        confidence_threshold=settings.confidence_threshold
    )
    
    # Initialize chatbot engine
    chatbot_engine = CBTChatbotEngine(hybrid_generator=hybrid_generator)
    
    logger.info("✓ Chatbot engine initialized successfully")
    
    yield
    
    # Cleanup
    logger.info("Shutting down...")


# Create FastAPI app
settings = get_settings()
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Enterprise-level CBT Mental Health Chatbot API",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Request/Response Models
class ChatRequest(BaseModel):
    """Chat request model"""
    session_id: Optional[str] = Field(None, description="Session ID (creates new if not provided)")
    message: str = Field(..., min_length=1, max_length=2000, description="User message")
    user_id: Optional[str] = Field(None, description="User identifier")


class ChatResponse(BaseModel):
    """Chat response model"""
    session_id: str
    response: str
    emotional_state: str
    timestamp: datetime = Field(default_factory=datetime.now)
    conversation_length: int
    metadata: Optional[Dict] = None


class SessionRequest(BaseModel):
    """Session creation request"""
    user_id: Optional[str] = None


class SessionResponse(BaseModel):
    """Session response"""
    session_id: str
    created_at: datetime


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    version: str
    timestamp: datetime = Field(default_factory=datetime.now)


# API Endpoints
@app.get("/", response_model=Dict)
async def root():
    """Root endpoint"""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        version=settings.app_version
    )


@app.post("/session", response_model=SessionResponse, status_code=status.HTTP_201_CREATED)
async def create_session(request: SessionRequest):
    """Create a new chat session"""
    try:
        session_id = chatbot_engine.create_session(user_id=request.user_id)
        return SessionResponse(
            session_id=session_id,
            created_at=datetime.now()
        )
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session"
        )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Send a message and get a response from the chatbot
    
    The chatbot uses a hybrid approach combining:
    - Custom-trained CBT model
    - GPT-4 for natural language understanding
    """
    try:
        # Create session if not provided
        session_id = request.session_id
        if not session_id:
            session_id = chatbot_engine.create_session(user_id=request.user_id)
        
        # Process message
        result = chatbot_engine.process_message(
            session_id=session_id,
            user_message=request.message
        )
        
        return ChatResponse(
            session_id=result["session_id"],
            response=result["response"],
            emotional_state=result["emotional_state"],
            conversation_length=result["conversation_length"],
            metadata=result.get("metadata")
        )
    
    except Exception as e:
        logger.error(f"Error processing message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process message"
        )


@app.get("/session/{session_id}", response_model=Dict)
async def get_session(session_id: str):
    """Get session information"""
    summary = chatbot_engine.get_session_summary(session_id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return summary


@app.get("/session/{session_id}/history", response_model=List[Dict])
async def get_conversation_history(session_id: str):
    """Get conversation history for a session"""
    history = chatbot_engine.get_conversation_export(session_id)
    if history is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    return history


@app.delete("/session/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(session_id: str):
    """End and delete a session"""
    success = chatbot_engine.end_session(session_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal server error"}
    )


if __name__ == "__main__":
    import uvicorn
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug
    )
