"""
Free API Response Generator using Google Gemini

Google Gemini API is FREE with generous limits:
- 15 requests per minute
- 1 million tokens per minute
- 1,500 requests per day
"""
import logging
from typing import Dict, List, Optional
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)


class FreeAPIGenerator:
    """Generate responses using free Google Gemini API"""
    
    def __init__(self, api_key: str, model_name: str = "gemini-2.0-flash-exp"):
        """
        Initialize Gemini API
        
        Args:
            api_key: Google Gemini API key (free from https://aistudio.google.com/apikey)
            model_name: Model to use (gemini-2.0-flash-exp is free and fast)
        """
        self.client = genai.Client(api_key=api_key)
        self.model_name = model_name
        logger.info(f"Initialized free Gemini API: {model_name}")
    
    def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        session_context: Optional[Dict] = None
    ) -> str:
        """
        Generate CBT response using free Gemini API
        
        Args:
            user_message: Current user input
            conversation_history: Previous conversation turns
            session_context: Additional session information
            
        Returns:
            Generated response text
        """
        try:
            # Build prompt with CBT context
            prompt = self._build_prompt(user_message, conversation_history, session_context)
            
            # Generate response
            response = self.client.models.generate_content(
                model=self.model_name,
                contents=prompt
            )
            
            return response.text
            
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return "I understand you're going through a difficult time. Let's work through this together using some CBT techniques. Can you tell me more about the specific thoughts or feelings you're experiencing right now?"
    
    def _build_prompt(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        session_context: Optional[Dict] = None
    ) -> str:
        """Build comprehensive prompt with CBT context"""
        
        system_context = """You are an empathetic and knowledgeable CBT (Cognitive Behavioral Therapy) mental health assistant. Your role is to:

1. Provide supportive, evidence-based responses using CBT principles
2. Help users identify and challenge negative thought patterns (cognitive distortions like catastrophizing, black-and-white thinking, etc.)
3. Encourage behavioral activation and healthy coping strategies
4. Show empathy and validate emotions while guiding toward solutions
5. Ask clarifying questions to better understand the user's situation
6. Suggest practical CBT techniques when appropriate (thought records, behavioral experiments, exposure therapy, etc.)

Important guidelines:
- Always be supportive, warm, and non-judgmental
- Use CBT frameworks actively (identify automatic thoughts, challenge distortions, reframe thinking)
- Provide specific actionable advice and coping strategies
- Encourage professional help for serious mental health concerns
- Maintain appropriate boundaries
- Focus on empowerment and skill-building
- Keep responses conversational and under 150 words

CBT Techniques to use:
- Cognitive restructuring (identify and challenge negative thoughts)
- Behavioral activation (encourage action to improve mood)
- Exposure therapy principles (gradual facing of fears)
- Mindfulness and grounding techniques
- Problem-solving strategies
- Relaxation and breathing exercises

Remember: You are a supportive CBT tool, not a replacement for professional therapy. Provide practical, actionable guidance."""

        # Build conversation context
        prompt = f"{system_context}\n\n"
        
        # Add recent conversation history (last 3 turns)
        if conversation_history:
            prompt += "Previous conversation:\n"
            for turn in conversation_history[-3:]:
                user_msg = turn.get("user", "")
                asst_msg = turn.get("assistant", "")
                if user_msg:
                    prompt += f"User: {user_msg}\n"
                if asst_msg:
                    prompt += f"Assistant: {asst_msg}\n"
            prompt += "\n"
        
        # Add current message
        prompt += f"User: {user_message}\n\nAssistant:"
        
        return prompt
