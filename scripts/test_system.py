"""
Test Script

Quick test of the chatbot system without full setup.
Uses mock models for demonstration.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import logging
from typing import List, Dict, Tuple

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MockCBTModel:
    """Mock CBT model for testing"""
    
    def generate(self, user_message: str, conversation_history: List[Dict[str, str]]) -> Tuple[str, float]:
        """Generate a mock response"""
        responses = {
            "anxious": ("It sounds like you're experiencing anxiety. Let's work on identifying the thoughts behind these feelings. Can you tell me what specific worries are coming up?", 0.85),
            "depressed": ("I hear that you're feeling down. Depression can make everything feel harder. Let's explore what might be contributing to these feelings.", 0.80),
            "default": ("Thank you for sharing that with me. I'm here to listen and support you. Can you tell me more about what's been on your mind?", 0.75)
        }
        
        message_lower = user_message.lower()
        if any(word in message_lower for word in ['anxious', 'anxiety', 'worried', 'nervous']):
            return responses['anxious']
        elif any(word in message_lower for word in ['depressed', 'sad', 'down', 'hopeless']):
            return responses['depressed']
        else:
            return responses['default']


def test_basic_functionality():
    """Test basic chatbot functionality"""
    print("\n" + "="*70)
    print(" Testing CBT Chatbot - Basic Functionality ".center(70))
    print("="*70 + "\n")
    
    from src.core.chatbot_engine import CBTChatbotEngine
    from src.core.hybrid_generator import HybridResponseGenerator
    
    # Mock components
    mock_model = MockCBTModel()
    
    # For testing without OpenAI, create a simple mock hybrid generator
    class MockHybridGenerator:
        def __init__(self, custom_model):
            self.custom_model = custom_model
        
        def generate_response(self, user_message, conversation_history, session_context=None):
            response, _ = self.custom_model.generate(user_message, conversation_history)
            return response
        
        def get_response_metadata(self, response):
            return {"length": len(response), "word_count": len(response.split())}
    
    # Initialize engine with mock generator
    hybrid_gen = MockHybridGenerator(mock_model)
    chatbot = CBTChatbotEngine(hybrid_generator=hybrid_gen)
    
    # Create session
    session_id = chatbot.create_session()
    print(f"✓ Created session: {session_id}\n")
    
    # Test messages
    test_messages = [
        "I'm feeling really anxious about my job interview tomorrow.",
        "I've been feeling depressed lately and don't want to do anything.",
        "Can you help me with stress management?",
    ]
    
    for msg in test_messages:
        print(f"User: {msg}")
        result = chatbot.process_message(session_id, msg)
        print(f"Bot: {result['response']}")
        print(f"Emotional State: {result['emotional_state']}")
        print(f"Conversation Length: {result['conversation_length']}\n")
        print("-" * 70 + "\n")
    
    # Get session summary
    summary = chatbot.get_session_summary(session_id)
    print("Session Summary:")
    print(f"  Messages: {summary['message_count']}")
    print(f"  Duration: {summary['duration_minutes']} minutes")
    
    print("\n✓ All tests passed!\n")


def test_dataset_loading():
    """Test dataset loading"""
    print("\n" + "="*70)
    print(" Testing Dataset Loading ".center(70))
    print("="*70 + "\n")
    
    try:
        from src.data.dataset_manager import CBTDatasetManager
        
        manager = CBTDatasetManager()
        print("Loading datasets...")
        df = manager.load_mental_health_datasets()
        
        print(f"\n✓ Loaded {len(df)} conversations")
        print(f"\nDataset columns: {list(df.columns)}")
        print(f"\nSample conversation:")
        print(f"Context: {df.iloc[0]['context'][:100]}...")
        print(f"Response: {df.iloc[0]['response'][:100]}...")
        
    except Exception as e:
        print(f"Note: Dataset loading requires internet connection and datasets library")
        print(f"Error: {e}")


if __name__ == "__main__":
    print("\nRunning CBT Chatbot Tests...\n")
    
    # Test basic functionality
    test_basic_functionality()
    
    # Test dataset loading
    print("\n")
    test_dataset_loading()
    
    print("\n" + "="*70)
    print(" Testing Complete ".center(70))
    print("="*70 + "\n")
