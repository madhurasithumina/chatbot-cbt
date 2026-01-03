"""
Hybrid Response Generator

Combines responses from custom-trained CBT model and GPT-4 to generate
optimal therapeutic responses.
"""
import logging
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import numpy as np

logger = logging.getLogger(__name__)


@dataclass
class ResponseCandidate:
    """Container for a response candidate"""
    text: str
    confidence: float
    source: str
    reasoning: Optional[str] = None


class HybridResponseGenerator:
    """
    Generates responses by combining custom CBT model with GPT-4
    
    Architecture:
    1. Custom model generates CBT-specific response with confidence
    2. GPT-4 generates contextual response
    3. Responses are merged based on confidence and weights
    """
    
    def __init__(
        self,
        openai_api_key: str,
        custom_model,
        embedding_model_name: str = "sentence-transformers/all-MiniLM-L6-v2",
        custom_weight: float = 0.4,
        gpt_weight: float = 0.6,
        confidence_threshold: float = 0.7
    ):
        self.openai_client = OpenAI(api_key=openai_api_key)
        self.custom_model = custom_model
        self.embedding_model = SentenceTransformer(embedding_model_name)
        self.custom_weight = custom_weight
        self.gpt_weight = gpt_weight
        self.confidence_threshold = confidence_threshold
    
    def generate_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        session_context: Optional[Dict] = None
    ) -> str:
        """
        Generate hybrid response combining custom model and GPT
        
        Args:
            user_message: Current user input
            conversation_history: Previous conversation turns
            session_context: Additional session information
            
        Returns:
            Final merged response
        """
        # Generate response from custom CBT model
        custom_response = self._generate_custom_response(
            user_message, 
            conversation_history
        )
        
        # Generate response from GPT-4
        gpt_response = self._generate_gpt_response(
            user_message, 
            conversation_history,
            session_context
        )
        
        # Merge responses based on confidence and weights
        final_response = self._merge_responses(custom_response, gpt_response)
        
        logger.info(f"Generated hybrid response (custom conf: {custom_response.confidence:.2f})")
        
        return final_response
    
    def _generate_custom_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]]
    ) -> ResponseCandidate:
        """Generate response using custom-trained CBT model"""
        try:
            # Get response from custom model
            response_text, confidence = self.custom_model.generate(
                user_message,
                conversation_history
            )
            
            return ResponseCandidate(
                text=response_text,
                confidence=confidence,
                source="custom_cbt_model"
            )
        except Exception as e:
            logger.error(f"Custom model error: {e}")
            return ResponseCandidate(
                text="",
                confidence=0.0,
                source="custom_cbt_model"
            )
    
    def _generate_gpt_response(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        session_context: Optional[Dict] = None
    ) -> ResponseCandidate:
        """Generate response using GPT-4"""
        try:
            # Build conversation context
            messages = self._build_gpt_messages(
                user_message,
                conversation_history,
                session_context
            )
            
            # Call GPT-4
            response = self.openai_client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=messages,
                temperature=0.7,
                max_tokens=500
            )
            
            response_text = response.choices[0].message.content
            
            return ResponseCandidate(
                text=response_text,
                confidence=0.9,  # GPT typically high confidence
                source="gpt4"
            )
        except Exception as e:
            logger.error(f"GPT-4 error: {e}")
            return ResponseCandidate(
                text="I'm here to listen and support you. Could you tell me more about what you're experiencing?",
                confidence=0.5,
                source="gpt4_fallback"
            )
    
    def _build_gpt_messages(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        session_context: Optional[Dict] = None
    ) -> List[Dict[str, str]]:
        """Build message array for GPT API"""
        system_prompt = """You are an empathetic and knowledgeable CBT (Cognitive Behavioral Therapy) mental health chatbot. Your role is to:

1. Provide supportive, evidence-based responses using CBT principles
2. Help users identify and challenge negative thought patterns
3. Encourage behavioral activation and healthy coping strategies
4. Show empathy and validate emotions while guiding toward solutions
5. Ask clarifying questions to better understand the user's situation
6. Suggest practical CBT techniques when appropriate

Important guidelines:
- Always be supportive and non-judgmental
- Use CBT frameworks (identifying automatic thoughts, cognitive distortions, behavioral experiments)
- Encourage professional help for serious mental health concerns
- Maintain appropriate boundaries
- Focus on empowerment and skill-building

Remember: You are a supportive tool, not a replacement for professional therapy."""

        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history (last 5 turns for context)
        for turn in conversation_history[-5:]:
            messages.append({"role": "user", "content": turn.get("user", "")})
            messages.append({"role": "assistant", "content": turn.get("assistant", "")})
        
        # Add current message
        messages.append({"role": "user", "content": user_message})
        
        return messages
    
    def _merge_responses(
        self,
        custom_response: ResponseCandidate,
        gpt_response: ResponseCandidate
    ) -> str:
        """
        Merge responses based on confidence and weights
        
        Strategy:
        1. If custom model has high confidence (>threshold), blend responses
        2. If custom model has low confidence, prefer GPT
        3. Use semantic similarity to avoid redundancy
        """
        # If custom model has very low confidence, use GPT
        if custom_response.confidence < 0.3:
            return gpt_response.text
        
        # If custom model has high confidence, create hybrid
        if custom_response.confidence >= self.confidence_threshold:
            return self._create_hybrid_response(custom_response, gpt_response)
        
        # Medium confidence: prefer GPT but validate against custom
        return gpt_response.text
    
    def _create_hybrid_response(
        self,
        custom_response: ResponseCandidate,
        gpt_response: ResponseCandidate
    ) -> str:
        """
        Create a hybrid response combining both models
        
        Uses the custom CBT model's specific techniques while incorporating
        GPT's natural language and empathy.
        """
        # Calculate semantic similarity
        custom_embedding = self.embedding_model.encode([custom_response.text])[0]
        gpt_embedding = self.embedding_model.encode([gpt_response.text])[0]
        
        similarity = np.dot(custom_embedding, gpt_embedding) / (
            np.linalg.norm(custom_embedding) * np.linalg.norm(gpt_embedding)
        )
        
        # If responses are very similar, use the one with higher confidence
        if similarity > 0.85:
            if custom_response.confidence > 0.8:
                return custom_response.text
            return gpt_response.text
        
        # If responses are different, combine them intelligently
        # Use GPT as primary with custom model insights
        if len(custom_response.text) > 50:  # Has substantial content
            hybrid = f"{gpt_response.text}\n\n{custom_response.text}"
            return hybrid
        
        return gpt_response.text
    
    def get_response_metadata(self, response: str) -> Dict:
        """Get metadata about the generated response"""
        return {
            "length": len(response),
            "word_count": len(response.split()),
            "has_question": "?" in response,
            "embedding": self.embedding_model.encode([response])[0].tolist()
        }
