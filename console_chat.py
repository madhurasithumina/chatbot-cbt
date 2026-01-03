"""
Simple Console Interface for CBT Chatbot

Interactive command-line interface for testing the chatbot.
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent))

import logging
from src.core.chatbot_engine import CBTChatbotEngine
from src.core.hybrid_generator import HybridResponseGenerator
from src.models.cbt_model import CBTModel
from config.config import get_settings

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner():
    """Print welcome banner"""
    print("\n" + "="*70)
    print(" CBT Mental Health Chatbot - Interactive Console ".center(70))
    print("="*70)
    print("\nWelcome! I'm here to support you using CBT techniques.")
    print("Type 'quit' or 'exit' to end the conversation.")
    print("Type 'help' for available commands.")
    print("="*70 + "\n")


def print_help():
    """Print help information"""
    print("\n" + "-"*70)
    print(" Available Commands ".center(70))
    print("-"*70)
    print("  quit/exit   - End the conversation")
    print("  help        - Show this help message")
    print("  history     - Show conversation history")
    print("  clear       - Start a new session")
    print("  summary     - Show session summary")
    print("-"*70 + "\n")


def main():
    """Main console application"""
    print_banner()
    
    # Load settings
    settings = get_settings()
    
    # Initialize chatbot engine
    print("Initializing chatbot engine...")
    try:
        # Initialize custom model
        cbt_model = CBTModel(
            model_path=settings.custom_model_path if Path(settings.custom_model_path).exists() else None
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
        chatbot = CBTChatbotEngine(hybrid_generator=hybrid_generator)
        
        # Create session
        session_id = chatbot.create_session()
        
        print("✓ Chatbot ready!\n")
        
    except Exception as e:
        print(f"✗ Error initializing chatbot: {e}")
        print("\nPlease ensure:")
        print("1. You have created a .env file with your OPENAI_API_KEY")
        print("2. All dependencies are installed: pip install -r requirements.txt")
        return
    
    # Main conversation loop
    while True:
        try:
            # Get user input
            user_input = input("\n💭 You: ").strip()
            
            if not user_input:
                continue
            
            # Handle commands
            if user_input.lower() in ['quit', 'exit']:
                print("\n🌟 Take care! Remember, seeking professional help is always a good step.")
                break
            
            elif user_input.lower() == 'help':
                print_help()
                continue
            
            elif user_input.lower() == 'history':
                history = chatbot.get_conversation_export(session_id)
                if history:
                    print("\n📜 Conversation History:")
                    for i, turn in enumerate(history, 1):
                        print(f"\n{i}. You: {turn['user']}")
                        print(f"   Bot: {turn['assistant']}")
                else:
                    print("\n📜 No conversation history yet.")
                continue
            
            elif user_input.lower() == 'clear':
                session_id = chatbot.create_session()
                print("\n🔄 Started new session.")
                continue
            
            elif user_input.lower() == 'summary':
                summary = chatbot.get_session_summary(session_id)
                if summary:
                    print("\n📊 Session Summary:")
                    print(f"   Messages: {summary['message_count']}")
                    print(f"   Duration: {summary['duration_minutes']} minutes")
                continue
            
            # Process message
            print("\n🤖 Bot: ", end="", flush=True)
            result = chatbot.process_message(session_id, user_input)
            print(result['response'])
            
        except KeyboardInterrupt:
            print("\n\n🌟 Take care!")
            break
        except Exception as e:
            logger.error(f"Error: {e}")
            print("\n❌ Sorry, I encountered an error. Please try again.")


if __name__ == "__main__":
    main()
