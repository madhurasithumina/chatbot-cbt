"""
Custom CBT Model

Neural model trained on mental health conversations for generating
CBT-specific therapeutic responses.
"""
import torch
import torch.nn as nn
from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    TrainingArguments,
    Trainer,
    DataCollatorForLanguageModeling
)
from typing import List, Dict, Tuple, Optional
import logging
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)


class CBTModel:
    """
    Custom CBT model based on fine-tuned transformer
    
    Uses a pre-trained model (e.g., GPT-2, Llama) fine-tuned on
    mental health conversations for CBT-specific responses.
    """
    
    def __init__(
        self,
        model_name: str = "microsoft/DialoGPT-medium",
        model_path: Optional[str] = None,
        device: str = "cuda" if torch.cuda.is_available() else "cpu"
    ):
        self.device = device
        self.model_name = model_name
        
        # Load tokenizer
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        
        # Set padding token if not exists
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token
        
        # Load model
        if model_path and Path(model_path).exists():
            logger.info(f"Loading model from {model_path}")
            self.model = AutoModelForCausalLM.from_pretrained(model_path)
        else:
            logger.info(f"Loading base model: {model_name}")
            self.model = AutoModelForCausalLM.from_pretrained(model_name)
        
        self.model.to(self.device)
        self.model.eval()
    
    def generate(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        max_length: int = 150,
        temperature: float = 0.8,
        top_p: float = 0.9
    ) -> Tuple[str, float]:
        """
        Generate response with confidence score
        
        Args:
            user_message: Current user input
            conversation_history: Previous conversation turns
            max_length: Maximum response length
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            
        Returns:
            Tuple of (response_text, confidence_score)
        """
        try:
            # Build conversation context
            context = self._build_context(user_message, conversation_history)
            
            # Tokenize input
            inputs = self.tokenizer.encode(
                context + self.tokenizer.eos_token,
                return_tensors="pt"
            ).to(self.device)
            
            # Generate response
            with torch.no_grad():
                outputs = self.model.generate(
                    inputs,
                    max_length=min(inputs.shape[1] + max_length, 512),
                    temperature=temperature,
                    top_p=top_p,
                    do_sample=True,
                    pad_token_id=self.tokenizer.pad_token_id,
                    num_return_sequences=1,
                    output_scores=True,
                    return_dict_in_generate=True
                )
            
            # Decode response
            generated_ids = outputs.sequences[0][inputs.shape[1]:]
            response = self.tokenizer.decode(generated_ids, skip_special_tokens=True)
            
            # Calculate confidence from generation scores
            confidence = self._calculate_confidence(outputs.scores)
            
            # Clean response
            response = self._clean_response(response)
            
            return response, confidence
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return "", 0.0
    
    def _build_context(
        self,
        user_message: str,
        conversation_history: List[Dict[str, str]],
        max_turns: int = 3
    ) -> str:
        """Build conversation context from history"""
        context_parts = []
        
        # Add recent history (last N turns)
        for turn in conversation_history[-max_turns:]:
            if "user" in turn:
                context_parts.append(f"User: {turn['user']}")
            if "assistant" in turn:
                context_parts.append(f"Therapist: {turn['assistant']}")
        
        # Add current message
        context_parts.append(f"User: {user_message}")
        context_parts.append("Therapist:")
        
        return " ".join(context_parts)
    
    def _calculate_confidence(self, scores: Tuple[torch.Tensor]) -> float:
        """
        Calculate confidence score from generation probabilities
        
        Uses mean of top token probabilities across generation steps
        """
        if not scores:
            return 0.5
        
        try:
            # Convert scores to probabilities
            probs = [torch.softmax(score, dim=-1) for score in scores]
            
            # Get max probability at each step
            max_probs = [prob.max().item() for prob in probs]
            
            # Average confidence
            confidence = np.mean(max_probs)
            
            return float(confidence)
        except Exception as e:
            logger.warning(f"Error calculating confidence: {e}")
            return 0.5
    
    def _clean_response(self, response: str) -> str:
        """Clean and validate generated response"""
        # Remove any remaining special tokens
        response = response.strip()
        
        # Remove incomplete sentences at the end
        if response and not response[-1] in '.!?':
            # Find last sentence boundary
            last_period = max(
                response.rfind('.'),
                response.rfind('!'),
                response.rfind('?')
            )
            if last_period > len(response) // 2:  # Only if substantial content remains
                response = response[:last_period + 1]
        
        # Ensure reasonable length
        if len(response) < 10:
            return ""
        
        return response
    
    def train(
        self,
        train_dataset,
        eval_dataset,
        output_dir: str,
        num_epochs: int = 3,
        batch_size: int = 4,
        learning_rate: float = 2e-5
    ):
        """
        Fine-tune the model on CBT conversation data
        
        Args:
            train_dataset: Training dataset
            eval_dataset: Evaluation dataset
            output_dir: Directory to save model
            num_epochs: Number of training epochs
            batch_size: Training batch size
            learning_rate: Learning rate
        """
        logger.info("Starting model training...")
        
        # Training arguments
        training_args = TrainingArguments(
            output_dir=output_dir,
            num_train_epochs=num_epochs,
            per_device_train_batch_size=batch_size,
            per_device_eval_batch_size=batch_size,
            learning_rate=learning_rate,
            warmup_steps=500,
            weight_decay=0.01,
            logging_dir=f"{output_dir}/logs",
            logging_steps=100,
            eval_strategy="epoch",
            save_strategy="epoch",
            load_best_model_at_end=True,
            metric_for_best_model="eval_loss",
            gradient_accumulation_steps=2,
            fp16=torch.cuda.is_available(),
        )
        
        # Data collator
        data_collator = DataCollatorForLanguageModeling(
            tokenizer=self.tokenizer,
            mlm=False
        )
        
        # Initialize trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            data_collator=data_collator
        )
        
        # Train
        trainer.train()
        
        # Save model
        trainer.save_model(output_dir)
        self.tokenizer.save_pretrained(output_dir)
        
        logger.info(f"Model saved to {output_dir}")
    
    def save(self, path: str):
        """Save model to disk"""
        Path(path).mkdir(parents=True, exist_ok=True)
        self.model.save_pretrained(path)
        self.tokenizer.save_pretrained(path)
        logger.info(f"Model saved to {path}")
    
    def load(self, path: str):
        """Load model from disk"""
        self.model = AutoModelForCausalLM.from_pretrained(path)
        self.tokenizer = AutoTokenizer.from_pretrained(path)
        self.model.to(self.device)
        self.model.eval()
        logger.info(f"Model loaded from {path}")
