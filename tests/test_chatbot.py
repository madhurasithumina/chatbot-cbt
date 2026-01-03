"""
Unit tests for CBT Chatbot components
"""
import pytest
from src.core.chatbot_engine import CBTChatbotEngine, ChatSession, EmotionalState
from typing import List, Dict, Tuple


class MockModel:
    """Mock model for testing"""
    
    def generate(self, message: str, history: List[Dict]) -> Tuple[str, float]:
        return "This is a test response", 0.85


class MockHybridGenerator:
    """Mock hybrid generator for testing"""
    
    def __init__(self):
        self.custom_model = MockModel()
    
    def generate_response(self, user_message, conversation_history, session_context=None):
        return "This is a test response from hybrid generator"
    
    def get_response_metadata(self, response):
        return {"length": len(response), "word_count": len(response.split())}


def test_session_creation():
    """Test session creation"""
    session = ChatSession(session_id="test-123", user_id="user-1")
    assert session.session_id == "test-123"
    assert session.user_id == "user-1"
    assert len(session.conversation_history) == 0


def test_session_add_turn():
    """Test adding conversation turn to session"""
    session = ChatSession(session_id="test-123", user_id="user-1")
    session.add_turn("Hello", "Hi there!", EmotionalState.NEUTRAL, 0.9)
    
    assert len(session.conversation_history) == 1
    assert session.conversation_history[0].user_message == "Hello"
    assert session.conversation_history[0].bot_response == "Hi there!"


def test_chatbot_engine_create_session():
    """Test chatbot engine session creation"""
    generator = MockHybridGenerator()
    engine = CBTChatbotEngine(hybrid_generator=generator)
    
    session_id = engine.create_session(user_id="test-user")
    assert session_id is not None
    assert len(session_id) > 0


def test_chatbot_engine_process_message():
    """Test processing a message"""
    generator = MockHybridGenerator()
    engine = CBTChatbotEngine(hybrid_generator=generator)
    
    session_id = engine.create_session()
    result = engine.process_message(session_id, "I'm feeling anxious")
    
    assert "response" in result
    assert result["session_id"] == session_id
    assert result["conversation_length"] == 1


def test_chatbot_engine_conversation_history():
    """Test conversation history"""
    generator = MockHybridGenerator()
    engine = CBTChatbotEngine(hybrid_generator=generator)
    
    session_id = engine.create_session()
    
    # Send multiple messages
    engine.process_message(session_id, "Hello")
    engine.process_message(session_id, "I need help")
    engine.process_message(session_id, "Thank you")
    
    # Get history
    history = engine.get_conversation_export(session_id)
    assert len(history) == 3
    assert history[0]["user"] == "Hello"


def test_chatbot_engine_session_summary():
    """Test session summary"""
    generator = MockHybridGenerator()
    engine = CBTChatbotEngine(hybrid_generator=generator)
    
    session_id = engine.create_session()
    engine.process_message(session_id, "Test message")
    
    summary = engine.get_session_summary(session_id)
    assert summary is not None
    assert summary["message_count"] == 1
    assert "session_id" in summary


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
