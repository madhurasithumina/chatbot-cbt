"""
Mental Health / CBT Dataset Manager

This module handles loading and processing mental health conversation datasets
for training the CBT chatbot model.
"""
import json
import pandas as pd
from pathlib import Path
from typing import List, Dict, Tuple
from datasets import load_dataset
import logging

logger = logging.getLogger(__name__)


class CBTDatasetManager:
    """Manages CBT and mental health datasets"""
    
    def __init__(self, data_dir: str = "./data"):
        self.data_dir = Path(data_dir)
        self.raw_dir = self.data_dir / "raw"
        self.processed_dir = self.data_dir / "processed"
        
        # Create directories
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)
    
    def load_mental_health_datasets(self) -> pd.DataFrame:
        """
        Load curated mental health and CBT conversation datasets
        
        Combines multiple sources:
        1. Counseling and Mental Health Conversations
        2. CBT-focused therapy dialogues
        3. Mental health support conversations
        """
        all_conversations = []
        
        # Dataset 1: Mental Health Counseling Conversations
        logger.info("Loading mental health counseling dataset...")
        try:
            # Using Amod/mental_health_counseling_conversations dataset
            dataset1 = load_dataset("Amod/mental_health_counseling_conversations", split="train")
            for item in dataset1:
                all_conversations.append({
                    'context': item.get('Context', ''),
                    'response': item.get('Response', ''),
                    'source': 'counseling',
                    'category': 'general'
                })
            logger.info(f"Loaded {len(dataset1)} counseling conversations")
        except Exception as e:
            logger.warning(f"Could not load counseling dataset: {e}")
        
        # Dataset 2: Mental Health Conversational Data
        logger.info("Loading mental health conversational dataset...")
        try:
            dataset2 = load_dataset("heliosbrahma/mental_health_conversational_data", split="train")
            for item in dataset2:
                all_conversations.append({
                    'context': item.get('prompt', item.get('input', '')),
                    'response': item.get('response', item.get('output', '')),
                    'source': 'conversational',
                    'category': 'mental_health'
                })
            logger.info(f"Loaded {len(dataset2)} conversational entries")
        except Exception as e:
            logger.warning(f"Could not load conversational dataset: {e}")
        
        # Dataset 3: Therapy-focused conversations
        logger.info("Adding CBT-specific examples...")
        cbt_examples = self._get_cbt_examples()
        all_conversations.extend(cbt_examples)
        
        # Convert to DataFrame
        df = pd.DataFrame(all_conversations)
        
        # Clean and validate
        df = self._clean_dataset(df)
        
        logger.info(f"Total conversations loaded: {len(df)}")
        return df
    
    def _get_cbt_examples(self) -> List[Dict]:
        """Get CBT-specific conversation examples"""
        return [
            {
                'context': "I'm feeling really anxious about my upcoming presentation at work. I can't stop thinking about all the things that could go wrong.",
                'response': "It sounds like you're experiencing anticipatory anxiety. Let's explore this together. What specific thoughts are going through your mind about the presentation? CBT helps us identify these automatic thoughts and examine whether they're based on facts or assumptions. Can you tell me what you think might happen?",
                'source': 'cbt_curated',
                'category': 'anxiety'
            },
            {
                'context': "I always mess things up. I'm just not good enough at anything.",
                'response': "I hear that you're feeling discouraged. These sound like what we call 'all-or-nothing' thoughts in CBT. Let's challenge this together. Can you think of a recent situation where things went well, even if it was something small? It's important to look at the evidence both for and against these thoughts.",
                'source': 'cbt_curated',
                'category': 'depression'
            },
            {
                'context': "I've been feeling down lately and don't have motivation to do anything.",
                'response': "Thank you for sharing that with me. Low motivation and feeling down are common challenges. In CBT, we often find that inactivity can maintain low mood. Let's work together on behavioral activation - starting with small, manageable activities. What's one small thing you used to enjoy that we could set as a goal?",
                'source': 'cbt_curated',
                'category': 'depression'
            },
            {
                'context': "Everyone must think I'm weird. I'm too anxious to talk in social situations.",
                'response': "Social anxiety can be really challenging. Let's examine this thought: 'Everyone must think I'm weird.' In CBT, we call this mind reading - assuming we know what others think. What evidence do you have that people think you're weird? Have you received feedback that suggests this, or might this be your anxiety talking?",
                'source': 'cbt_curated',
                'category': 'social_anxiety'
            },
            {
                'context': "I can't sleep at night. My mind keeps racing with worries.",
                'response': "Racing thoughts at night are very common and exhausting. Let's try some CBT techniques for this. First, we can work on cognitive strategies like writing down your worries before bed to 'park' them. We can also explore sleep hygiene and relaxation techniques. What time do you usually go to bed, and what are your thoughts typically about?",
                'source': 'cbt_curated',
                'category': 'insomnia'
            },
            {
                'context': "I made a mistake at work and now I feel like I'm going to get fired.",
                'response': "It's understandable to feel worried after making a mistake. Let's use CBT to examine this more closely. This sounds like catastrophic thinking - jumping to the worst possible outcome. What actually happened, and what evidence do you have that you'll be fired? Have you been given feedback about your overall performance?",
                'source': 'cbt_curated',
                'category': 'work_stress'
            },
            {
                'context': "What is CBT and how can it help me?",
                'response': "Cognitive Behavioral Therapy (CBT) is an evidence-based approach that helps you understand the connections between your thoughts, feelings, and behaviors. It works on the principle that our thoughts influence how we feel and act. By identifying and challenging unhelpful thought patterns, we can improve our emotional well-being and develop healthier coping strategies. CBT is highly effective for anxiety, depression, and many other mental health challenges.",
                'source': 'cbt_curated',
                'category': 'psychoeducation'
            },
            {
                'context': "I keep procrastinating and then feel guilty about it.",
                'response': "Procrastination often creates a cycle of stress and guilt. In CBT, we look at what thoughts and beliefs might be driving the procrastination. Sometimes it's perfectionism ('It has to be perfect'), fear of failure, or feeling overwhelmed. Let's identify what thoughts come up when you're about to start a task. We can then work on breaking tasks into smaller steps and challenging those unhelpful thoughts.",
                'source': 'cbt_curated',
                'category': 'procrastination'
            }
        ]
    
    def _clean_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """Clean and validate dataset"""
        # Remove empty entries
        df = df.dropna(subset=['context', 'response'])
        df = df[df['context'].str.strip() != '']
        df = df[df['response'].str.strip() != '']
        
        # Remove duplicates
        df = df.drop_duplicates(subset=['context', 'response'])
        
        # Filter out very short responses (likely low quality)
        df = df[df['response'].str.len() > 20]
        
        return df
    
    def save_processed_data(self, df: pd.DataFrame, filename: str = "processed_conversations.csv"):
        """Save processed dataset"""
        filepath = self.processed_dir / filename
        df.to_csv(filepath, index=False)
        logger.info(f"Saved processed data to {filepath}")
        return filepath
    
    def prepare_training_data(self, df: pd.DataFrame, 
                            test_size: float = 0.2) -> Tuple[pd.DataFrame, pd.DataFrame]:
        """Split data into training and validation sets"""
        from sklearn.model_selection import train_test_split
        
        train_df, val_df = train_test_split(
            df, 
            test_size=test_size, 
            random_state=42,
            stratify=df['category'] if 'category' in df.columns else None
        )
        
        logger.info(f"Training samples: {len(train_df)}, Validation samples: {len(val_df)}")
        return train_df, val_df


def main():
    """Test dataset loading"""
    logging.basicConfig(level=logging.INFO)
    
    manager = CBTDatasetManager()
    df = manager.load_mental_health_datasets()
    
    print(f"\nDataset Statistics:")
    print(f"Total conversations: {len(df)}")
    print(f"\nSample conversation:")
    print(f"Context: {df.iloc[0]['context']}")
    print(f"Response: {df.iloc[0]['response']}")
    
    # Save processed data
    manager.save_processed_data(df)


if __name__ == "__main__":
    main()
