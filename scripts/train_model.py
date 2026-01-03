"""
Model Training Pipeline

Trains the custom CBT model on mental health conversation data.
"""
import sys
from pathlib import Path

# Add src to path
sys.path.append(str(Path(__file__).parent.parent))

import logging
import torch
from datasets import Dataset
from src.data.dataset_manager import CBTDatasetManager
from src.models.cbt_model import CBTModel

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def prepare_dataset_for_training(df, tokenizer, max_length=256):
    """Prepare dataset for model training"""
    
    def tokenize_function(examples):
        # Create conversation format: "User: {context} Therapist: {response}"
        texts = [
            f"User: {context} Therapist: {response}"
            for context, response in zip(examples['context'], examples['response'])
        ]
        
        # Tokenize
        tokenized = tokenizer(
            texts,
            truncation=True,
            max_length=max_length,
            padding='max_length',
            return_tensors='pt'
        )
        
        # For causal LM, labels are the same as input_ids
        tokenized['labels'] = tokenized['input_ids'].clone()
        
        return tokenized
    
    # Convert to Hugging Face dataset
    dataset = Dataset.from_pandas(df[['context', 'response']])
    
    # Tokenize
    tokenized_dataset = dataset.map(
        tokenize_function,
        batched=True,
        remove_columns=dataset.column_names
    )
    
    return tokenized_dataset


def main():
    """Main training pipeline"""
    logger.info("Starting CBT model training pipeline...")
    
    # Configuration
    MODEL_NAME = "microsoft/DialoGPT-medium"
    OUTPUT_DIR = "./data/models/cbt_model"
    NUM_EPOCHS = 3
    BATCH_SIZE = 4
    LEARNING_RATE = 2e-5
    
    # Step 1: Load dataset
    logger.info("Loading mental health datasets...")
    dataset_manager = CBTDatasetManager()
    df = dataset_manager.load_mental_health_datasets()
    
    logger.info(f"Loaded {len(df)} conversations")
    
    # Save processed data
    dataset_manager.save_processed_data(df)
    
    # Step 2: Split data
    logger.info("Splitting into train/validation sets...")
    train_df, val_df = dataset_manager.prepare_training_data(df, test_size=0.15)
    
    # Step 3: Initialize model
    logger.info(f"Initializing model: {MODEL_NAME}")
    cbt_model = CBTModel(model_name=MODEL_NAME)
    
    # Step 4: Prepare datasets for training
    logger.info("Preparing datasets...")
    train_dataset = prepare_dataset_for_training(train_df, cbt_model.tokenizer)
    val_dataset = prepare_dataset_for_training(val_df, cbt_model.tokenizer)
    
    # Step 5: Train model
    logger.info("Starting training...")
    cbt_model.train(
        train_dataset=train_dataset,
        eval_dataset=val_dataset,
        output_dir=OUTPUT_DIR,
        num_epochs=NUM_EPOCHS,
        batch_size=BATCH_SIZE,
        learning_rate=LEARNING_RATE
    )
    
    logger.info("Training completed!")
    
    # Step 6: Test model
    logger.info("\nTesting trained model...")
    test_messages = [
        "I'm feeling really anxious about my presentation tomorrow.",
        "I can't seem to get motivated to do anything.",
        "I think everyone at work doesn't like me.",
    ]
    
    for msg in test_messages:
        response, confidence = cbt_model.generate(msg, [])
        logger.info(f"\nUser: {msg}")
        logger.info(f"Bot (conf={confidence:.2f}): {response}")
    
    logger.info(f"\n✓ Model saved to {OUTPUT_DIR}")
    logger.info("Training pipeline completed successfully!")


if __name__ == "__main__":
    main()
