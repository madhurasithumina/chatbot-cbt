"""
CBT Chatbot Engine

Main chatbot orchestration engine that manages conversations,
session state, and coordinates the hybrid response generation.
"""
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import logging
from dataclasses import dataclass, field
from enum import Enum

logger = logging.getLogger(__name__)


class EmotionalState(Enum):
    """User's perceived emotional state"""
    ANXIOUS = "anxious"
    DEPRESSED = "depressed"
    STRESSED = "stressed"
    CALM = "calm"
    NEUTRAL = "neutral"
    UNKNOWN = "unknown"


@dataclass
class ConversationTurn:
    """Single conversation turn"""
    user_message: str
    bot_response: str
    timestamp: datetime = field(default_factory=datetime.now)
    emotional_state: EmotionalState = EmotionalState.UNKNOWN
    confidence: float = 0.0


@dataclass
class ChatSession:
    """Chat session state"""
    session_id: str
    user_id: Optional[str]
    conversation_history: List[ConversationTurn] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    last_active: datetime = field(default_factory=datetime.now)
    context: Dict = field(default_factory=dict)
    
    def add_turn(self, user_message: str, bot_response: str, 
                 emotional_state: EmotionalState = EmotionalState.UNKNOWN,
                 confidence: float = 0.0):
        """Add a conversation turn"""
        turn = ConversationTurn(
            user_message=user_message,
            bot_response=bot_response,
            emotional_state=emotional_state,
            confidence=confidence
        )
        self.conversation_history.append(turn)
        self.last_active = datetime.now()
    
    def get_recent_history(self, n: int = 5) -> List[Dict[str, str]]:
        """Get recent conversation history"""
        recent = self.conversation_history[-n:]
        return [
            {
                "user": turn.user_message,
                "assistant": turn.bot_response
            }
            for turn in recent
        ]


class CBTChatbotEngine:
    """
    Main CBT Chatbot Engine
    
    Orchestrates conversation flow, manages sessions, and coordinates
    the hybrid response generation system.
    """
    
    def __init__(self, hybrid_generator, sentiment_analyzer=None):
        self.hybrid_generator = hybrid_generator
        self.sentiment_analyzer = sentiment_analyzer
        self.sessions: Dict[str, ChatSession] = {}
    
    def create_session(self, user_id: Optional[str] = None) -> str:
        """Create a new chat session"""
        session_id = str(uuid.uuid4())
        session = ChatSession(
            session_id=session_id,
            user_id=user_id
        )
        self.sessions[session_id] = session
        logger.info(f"Created session {session_id}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[ChatSession]:
        """Get existing session"""
        return self.sessions.get(session_id)
    
    def process_message(
        self,
        session_id: str,
        user_message: str
    ) -> Dict[str, any]:
        """
        Process user message and generate response
        
        Args:
            session_id: Session identifier
            user_message: User's input message
            
        Returns:
            Dict containing response and metadata
        """
        # Get or create session
        session = self.get_session(session_id)
        if not session:
            logger.warning(f"Session {session_id} not found, creating new")
            session_id = self.create_session()
            session = self.get_session(session_id)
        
        # Detect emotional state (if analyzer available)
        emotional_state = EmotionalState.UNKNOWN
        if self.sentiment_analyzer:
            emotional_state = self._detect_emotional_state(user_message)
        
        # Get conversation history
        history = session.get_recent_history()
        
        # Generate response using hybrid generator
        response = self.hybrid_generator.generate_response(
            user_message=user_message,
            conversation_history=history,
            session_context=session.context
        )
        
        # Add turn to session
        session.add_turn(
            user_message=user_message,
            bot_response=response,
            emotional_state=emotional_state
        )
        
        # Get response metadata
        metadata = self.hybrid_generator.get_response_metadata(response)
        
        return {
            "session_id": session_id,
            "response": response,
            "emotional_state": emotional_state.value,
            "conversation_length": len(session.conversation_history),
            "metadata": metadata
        }
    
    def _detect_emotional_state(self, message: str) -> EmotionalState:
        """Detect user's emotional state from message"""
        if not self.sentiment_analyzer:
            return EmotionalState.UNKNOWN
        
        try:
            sentiment = self.sentiment_analyzer.analyze(message)
            
            # Map sentiment to emotional state
            if "anxiety" in sentiment or "anxious" in sentiment:
                return EmotionalState.ANXIOUS
            elif "depression" in sentiment or "sad" in sentiment:
                return EmotionalState.DEPRESSED
            elif "stress" in sentiment:
                return EmotionalState.STRESSED
            elif sentiment.get("positive", 0) > 0.7:
                return EmotionalState.CALM
            else:
                return EmotionalState.NEUTRAL
        except Exception as e:
            logger.error(f"Error detecting emotional state: {e}")
            return EmotionalState.UNKNOWN
    
    def get_session_summary(self, session_id: str) -> Optional[Dict]:
        """Get summary of session"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        return {
            "session_id": session.session_id,
            "created_at": session.created_at.isoformat(),
            "last_active": session.last_active.isoformat(),
            "message_count": len(session.conversation_history),
            "duration_minutes": (session.last_active - session.created_at).seconds // 60
        }
    
    def end_session(self, session_id: str) -> bool:
        """End and cleanup session"""
        if session_id in self.sessions:
            del self.sessions[session_id]
            logger.info(f"Ended session {session_id}")
            return True
        return False
    
    def get_conversation_export(self, session_id: str) -> Optional[List[Dict]]:
        """Export conversation history"""
        session = self.get_session(session_id)
        if not session:
            return None
        
        return [
            {
                "timestamp": turn.timestamp.isoformat(),
                "user": turn.user_message,
                "assistant": turn.bot_response,
                "emotional_state": turn.emotional_state.value
            }
            for turn in session.conversation_history
        ]
