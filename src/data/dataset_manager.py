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
            logger.info("Continuing with other data sources...")
        
        # Dataset 2: Alternative Mental Health Datasets
        logger.info("Loading additional mental health datasets...")
        alternative_datasets = [
            "Amod/mental_health_counseling_conversations",
            "mpingale/mental-health-chat-dataset"
        ]
        
        for dataset_name in alternative_datasets:
            try:
                dataset2 = load_dataset(dataset_name, split="train")
                for item in dataset2:
                    # Try different possible field names
                    context = item.get('prompt', item.get('input', item.get('question', item.get('Context', ''))))
                    response = item.get('response', item.get('output', item.get('answer', item.get('Response', ''))))
                    
                    if context and response:  # Only add if both exist
                        all_conversations.append({
                            'context': context,
                            'response': response,
                            'source': dataset_name.split('/')[-1],
                            'category': 'mental_health'
                        })
                logger.info(f"Loaded {len(dataset2)} entries from {dataset_name}")
                break  # Stop after first successful dataset
            except Exception as e:
                logger.warning(f"Could not load {dataset_name}: {e}")
                continue
        
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
            },
            {
                'context': "My partner and I keep having the same arguments over and over.",
                'response': "Repetitive conflicts often follow a pattern. In CBT, we can examine the thought patterns and behaviors that maintain this cycle. What do you think triggers these arguments? Understanding your automatic thoughts during conflicts can help us develop healthier communication patterns.",
                'source': 'cbt_curated',
                'category': 'relationships'
            },
            {
                'context': "I feel like I'm not good enough compared to others.",
                'response': "Comparing yourself to others is a common source of distress. This is called 'comparison thinking' in CBT. Remember that you're usually comparing your behind-the-scenes to everyone else's highlight reel. Let's work on identifying your own strengths and setting personal goals rather than comparing yourself to others.",
                'source': 'cbt_curated',
                'category': 'self_esteem'
            },
            {
                'context': "I have a big exam coming up and I'm panicking.",
                'response': "Exam anxiety is very common. Let's use some CBT strategies. First, let's identify the specific thoughts causing the panic. Are you catastrophizing about the outcome? Then we can work on practical preparation strategies and relaxation techniques. Breaking your study into manageable chunks can also help reduce overwhelm.",
                'source': 'cbt_curated',
                'category': 'anxiety'
            },
            {
                'context': "I don't enjoy things I used to love anymore.",
                'response': "Loss of interest in previously enjoyed activities is a common symptom of depression, called anhedonia. In CBT, we use behavioral activation to help rebuild these connections. Even when you don't feel like it, engaging in activities can help improve your mood. Let's start with small, achievable activities and gradually build up.",
                'source': 'cbt_curated',
                'category': 'depression'
            },
            {
                'context': "I'm worried about what people think of me all the time.",
                'response': "Constant worry about others' opinions can be exhausting. This involves 'mind reading' - assuming you know what others think. In reality, people are usually more focused on themselves than judging you. Let's work on building self-acceptance and challenging these assumptions with evidence.",
                'source': 'cbt_curated',
                'category': 'social_anxiety'
            },
            {
                'context': "I feel overwhelmed by everything I need to do.",
                'response': "Feeling overwhelmed often comes from trying to hold everything in your mind at once. Let's use a CBT technique: write down all your tasks, then prioritize them. Break larger tasks into smaller, manageable steps. Remember, you don't have to do everything at once. What's the most important task for today?",
                'source': 'cbt_curated',
                'category': 'stress'
            },
            {
                'context': "I made a mistake at work and I can't stop thinking about it.",
                'response': "Ruminating on mistakes is a common thinking pattern. In CBT, we call this 'mental filtering' - focusing only on the negative. Let's put this in perspective: What would you tell a friend in this situation? What have you learned from this? Everyone makes mistakes - they're opportunities for growth, not definitions of your worth.",
                'source': 'cbt_curated',
                'category': 'work_stress'
            },
            {
                'context': "I feel like giving up on everything.",
                'response': "Those feelings of hopelessness are very difficult, and I'm glad you're sharing this with me. These thoughts are symptoms of depression, not reality. While it feels overwhelming now, things can improve with support. Let's focus on small steps. Have you thought about harming yourself? If so, please reach out to a crisis helpline or mental health professional immediately.",
                'source': 'cbt_curated',
                'category': 'depression'
            },
            {
                'context': "How do I deal with negative thoughts?",
                'response': "Dealing with negative thoughts is central to CBT. First, notice when they occur. Then, examine the evidence for and against the thought. Ask yourself: Is this thought based on facts or feelings? What would I tell a friend thinking this? Finally, develop a more balanced, realistic thought. This takes practice, but it gets easier over time.",
                'source': 'cbt_curated',
                'category': 'psychoeducation'
            },
            {
                'context': "I'm having panic attacks and they're terrifying.",
                'response': "Panic attacks are frightening, but they're not dangerous, even though they feel that way. In CBT, we learn that panic attacks are your body's alarm system going off when there's no real danger. Let's work on breathing techniques, understanding the physical symptoms, and challenging the catastrophic thoughts that fuel the panic.",
                'source': 'cbt_curated',
                'category': 'panic'
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
        
        # Check if we have enough samples for stratification
        use_stratify = False
        if 'category' in df.columns and len(df) >= 10:
            # Check if each category has at least 2 samples
            category_counts = df['category'].value_counts()
            if category_counts.min() >= 2:
                use_stratify = True
        
        train_df, val_df = train_test_split(
            df, 
            test_size=test_size, 
            random_state=42,
            stratify=df['category'] if use_stratify else None
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
