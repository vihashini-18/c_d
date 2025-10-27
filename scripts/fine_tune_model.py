#!/usr/bin/env python3
"""
Fine-tune the medical chatbot model
"""

import os
import sys
import json
from pathlib import Path
from typing import List, Dict, Any

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.models.fine_tuning import MedicalFineTuner, create_sample_training_data
from config.settings import settings

def load_training_data(train_file: str, val_file: str) -> tuple:
    """Load training and validation data"""
    
    train_data = []
    val_data = []
    
    # Load training data
    if Path(train_file).exists():
        with open(train_file, 'r', encoding='utf-8') as f:
            for line in f:
                train_data.append(json.loads(line.strip()))
    else:
        print(f"❌ Training file not found: {train_file}")
        return None, None
    
    # Load validation data
    if Path(val_file).exists():
        with open(val_file, 'r', encoding='utf-8') as f:
            for line in f:
                val_data.append(json.loads(line.strip()))
    else:
        print(f"❌ Validation file not found: {val_file}")
        return None, None
    
    return train_data, val_data

def main():
    """Main fine-tuning function"""
    
    print("🚀 Fine-tuning Medical Chatbot Model...")
    print("=" * 50)
    
    # Check if training data exists
    train_file = "data/fine_tuning/train.jsonl"
    val_file = "data/fine_tuning/val.jsonl"
    
    if not Path(train_file).exists() or not Path(val_file).exists():
        print("❌ Training data not found. Creating sample data...")
        create_sample_training_data()
        print("✅ Sample training data created")
    
    # Load training data
    print("Loading training data...")
    train_data, val_data = load_training_data(train_file, val_file)
    
    if train_data is None or val_data is None:
        print("❌ Failed to load training data")
        return False
    
    print(f"✅ Loaded {len(train_data)} training samples")
    print(f"✅ Loaded {len(val_data)} validation samples")
    
    # Initialize fine-tuner
    print("Initializing fine-tuner...")
    fine_tuner = MedicalFineTuner()
    
    # Prepare datasets
    print("Preparing datasets...")
    train_dataset, val_dataset = fine_tuner.prepare_data(train_file, val_file)
    
    print(f"✅ Training dataset: {len(train_dataset)} samples")
    print(f"✅ Validation dataset: {len(val_dataset)} samples")
    
    # Fine-tune the model
    print("Starting fine-tuning...")
    print("This may take a while depending on your hardware...")
    
    try:
        output_dir = fine_tuner.fine_tune(
            train_dataset=train_dataset,
            val_dataset=val_dataset,
            output_dir="./fine_tuned_model",
            num_epochs=3,
            batch_size=4,
            learning_rate=5e-5
        )
        
        print(f"✅ Fine-tuning completed! Model saved to: {output_dir}")
        
        # Test the fine-tuned model
        print("\nTesting fine-tuned model...")
        test_questions = [
            "What are the symptoms of a heart attack?",
            "How can I prevent diabetes?",
            "What should I do if I have a fever?"
        ]
        
        for question in test_questions:
            print(f"\nQuestion: {question}")
            response = fine_tuner.generate_response(question)
            print(f"Answer: {response}")
        
        print("\n" + "=" * 50)
        print("✅ Fine-tuning completed successfully!")
        print(f"📁 Model saved to: {output_dir}")
        print("\nNext steps:")
        print("1. Update your model configuration to use the fine-tuned model")
        print("2. Test the model with the API")
        print("3. Deploy the updated model")
        
        return True
        
    except Exception as e:
        print(f"❌ Fine-tuning failed: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check if you have enough GPU memory")
        print("2. Try reducing batch_size or num_epochs")
        print("3. Ensure all dependencies are installed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
