#!/usr/bin/env python3
"""
Prepare fine-tuning data for medical chatbot
"""

import json
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
import pandas as pd

# Add the project root to the Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

def create_medical_qa_pairs() -> List[Dict[str, str]]:
    """Create medical Q&A pairs for fine-tuning"""
    
    medical_qa_data = [
        {
            "question": "What are the symptoms of a heart attack?",
            "answer": "Common symptoms of a heart attack include chest pain or discomfort, shortness of breath, pain in the arm, back, neck, or jaw, nausea, lightheadedness, and cold sweats. If you experience these symptoms, seek immediate medical attention."
        },
        {
            "question": "How can I prevent diabetes?",
            "answer": "To help prevent diabetes, maintain a healthy weight, eat a balanced diet with plenty of fruits and vegetables, exercise regularly, avoid smoking, and limit alcohol consumption. Regular check-ups with your doctor are also important."
        },
        {
            "question": "What should I do if I have a fever?",
            "answer": "For a fever, rest, stay hydrated, and take over-the-counter fever reducers like acetaminophen or ibuprofen as directed. If the fever is high (over 103°F), persistent, or accompanied by severe symptoms, consult a healthcare provider."
        },
        {
            "question": "What are the signs of dehydration?",
            "answer": "Signs of dehydration include thirst, dry mouth, dark yellow urine, fatigue, dizziness, confusion, and decreased urination. Severe dehydration can be dangerous and requires immediate medical attention."
        },
        {
            "question": "How do I know if I have high blood pressure?",
            "answer": "High blood pressure often has no symptoms, which is why it's called the 'silent killer.' Regular blood pressure checks are important. Symptoms, when present, may include headaches, shortness of breath, or nosebleeds."
        },
        {
            "question": "What should I do if I'm having chest pain?",
            "answer": "Chest pain can be serious and should not be ignored. If you have severe chest pain, especially with shortness of breath, nausea, or pain radiating to your arm or jaw, call 911 immediately. Even mild chest pain should be evaluated by a healthcare provider."
        },
        {
            "question": "How can I manage stress?",
            "answer": "To manage stress, try regular exercise, deep breathing exercises, meditation, getting enough sleep, maintaining a healthy diet, and talking to friends or a counselor. Avoid unhealthy coping mechanisms like excessive alcohol or smoking."
        },
        {
            "question": "What are the warning signs of a stroke?",
            "answer": "Warning signs of a stroke include sudden numbness or weakness in the face, arm, or leg (especially on one side), sudden confusion, trouble speaking or understanding, sudden trouble seeing, sudden trouble walking, dizziness, or severe headache. Call 911 immediately if you experience these symptoms."
        },
        {
            "question": "How often should I get a physical exam?",
            "answer": "Adults should generally have a physical exam once a year, or as recommended by their healthcare provider. The frequency may vary based on age, health status, and risk factors. Regular check-ups help detect health problems early."
        },
        {
            "question": "What are the benefits of regular exercise?",
            "answer": "Regular exercise helps maintain a healthy weight, strengthens the heart and muscles, improves mental health, reduces the risk of chronic diseases, improves sleep, and boosts energy levels. Aim for at least 150 minutes of moderate exercise per week."
        },
        {
            "question": "How can I improve my sleep quality?",
            "answer": "To improve sleep quality, maintain a regular sleep schedule, create a comfortable sleep environment, avoid caffeine and alcohol before bed, limit screen time before sleep, exercise regularly, and manage stress. If sleep problems persist, consult a healthcare provider."
        },
        {
            "question": "What should I do if I have a severe allergic reaction?",
            "answer": "If you have a severe allergic reaction (anaphylaxis), use an epinephrine auto-injector if available, call 911 immediately, lie down with legs elevated, and stay calm. Symptoms include difficulty breathing, swelling of the face or throat, rapid pulse, and dizziness."
        },
        {
            "question": "How can I prevent the flu?",
            "answer": "To prevent the flu, get an annual flu vaccine, wash your hands frequently, avoid close contact with sick people, cover your mouth when coughing or sneezing, and maintain a healthy lifestyle with proper nutrition and exercise."
        },
        {
            "question": "What are the symptoms of depression?",
            "answer": "Symptoms of depression include persistent sadness, loss of interest in activities, changes in appetite or weight, sleep disturbances, fatigue, difficulty concentrating, feelings of worthlessness, and thoughts of death or suicide. If you experience these symptoms, seek professional help."
        },
        {
            "question": "How can I maintain a healthy diet?",
            "answer": "To maintain a healthy diet, eat a variety of fruits and vegetables, choose whole grains, include lean proteins, limit processed foods, control portion sizes, stay hydrated, and limit added sugars and sodium. Consider consulting a nutritionist for personalized advice."
        }
    ]
    
    return medical_qa_data

def create_emergency_scenarios() -> List[Dict[str, str]]:
    """Create emergency scenario Q&A pairs"""
    
    emergency_data = [
        {
            "question": "I'm having severe chest pain and can't breathe properly. What should I do?",
            "answer": "This is a medical emergency. Call 911 immediately. While waiting for help, sit down and try to stay calm. If you have nitroglycerin prescribed by your doctor, take it as directed. Do not drive yourself to the hospital."
        },
        {
            "question": "My child has a high fever and is not responding normally. What should I do?",
            "answer": "This requires immediate medical attention. Call your pediatrician or go to the emergency room. In the meantime, try to keep your child cool with lukewarm baths and ensure they stay hydrated. Do not give aspirin to children with fever."
        },
        {
            "question": "I think I'm having a stroke. What are the signs and what should I do?",
            "answer": "If you experience sudden numbness or weakness in your face, arm, or leg (especially on one side), sudden confusion, trouble speaking, or severe headache, call 911 immediately. Time is critical for stroke treatment. Note the time when symptoms started."
        },
        {
            "question": "I'm having trouble breathing and my throat feels swollen. Is this an emergency?",
            "answer": "Yes, this could be a severe allergic reaction (anaphylaxis). Call 911 immediately. If you have an epinephrine auto-injector, use it right away. This is a life-threatening emergency that requires immediate treatment."
        },
        {
            "question": "I fell and hit my head. I'm feeling dizzy and nauseous. Should I go to the hospital?",
            "answer": "Yes, head injuries can be serious. Go to the emergency room immediately, especially if you have dizziness, nausea, confusion, or loss of consciousness. These could be signs of a concussion or more serious brain injury."
        }
    ]
    
    return emergency_data

def create_conversation_data() -> List[Dict[str, Any]]:
    """Create conversation-style data"""
    
    conversations = [
        {
            "conversation": [
                {
                    "role": "user",
                    "content": "I've been having headaches for the past week. Should I be worried?"
                },
                {
                    "role": "assistant",
                    "content": "Headaches can have various causes, from stress to more serious conditions. Since you've been experiencing them for a week, it's important to consult with a healthcare provider. In the meantime, try to identify any triggers like stress, lack of sleep, or certain foods. If you experience severe headaches, vision changes, or neck stiffness, seek immediate medical attention."
                }
            ]
        },
        {
            "conversation": [
                {
                    "role": "user",
                    "content": "What's the difference between a cold and the flu?"
                },
                {
                    "role": "assistant",
                    "content": "Colds and flu are both respiratory illnesses but are caused by different viruses. Colds typically have milder symptoms like runny nose, sneezing, and sore throat. Flu symptoms are usually more severe and include fever, body aches, fatigue, and can lead to serious complications. Flu symptoms come on more suddenly and are more intense than cold symptoms."
                }
            ]
        }
    ]
    
    return conversations

def save_training_data(data: List[Dict[str, str]], filename: str):
    """Save training data to JSONL format"""
    
    output_dir = Path("data/fine_tuning")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filepath = output_dir / filename
    
    with open(filepath, 'w', encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item, ensure_ascii=False) + '\n')
    
    print(f"✅ Saved {len(data)} items to {filepath}")

def create_train_val_split(data: List[Dict[str, str]], train_ratio: float = 0.8):
    """Split data into training and validation sets"""
    
    import random
    random.shuffle(data)
    
    split_idx = int(len(data) * train_ratio)
    train_data = data[:split_idx]
    val_data = data[split_idx:]
    
    return train_data, val_data

def main():
    """Main function to prepare fine-tuning data"""
    
    print("🚀 Preparing Fine-tuning Data for Medical Chatbot...")
    print("=" * 50)
    
    # Create data directories
    data_dir = Path("data/fine_tuning")
    data_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate different types of training data
    print("Creating medical Q&A pairs...")
    medical_qa = create_medical_qa_pairs()
    
    print("Creating emergency scenarios...")
    emergency_qa = create_emergency_scenarios()
    
    print("Creating conversation data...")
    conversations = create_conversation_data()
    
    # Combine all data
    all_qa_data = medical_qa + emergency_qa
    
    # Split into train/validation
    train_data, val_data = create_train_val_split(all_qa_data)
    
    # Save training data
    save_training_data(train_data, "train.jsonl")
    save_training_data(val_data, "val.jsonl")
    
    # Save conversation data
    save_training_data(conversations, "conversations.jsonl")
    
    # Create a summary
    summary = {
        "total_qa_pairs": len(all_qa_data),
        "training_pairs": len(train_data),
        "validation_pairs": len(val_data),
        "conversations": len(conversations),
        "medical_qa": len(medical_qa),
        "emergency_qa": len(emergency_qa)
    }
    
    with open(data_dir / "data_summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    
    print("\n" + "=" * 50)
    print("✅ Fine-tuning data preparation completed!")
    print(f"📊 Data Summary:")
    print(f"   - Total Q&A pairs: {summary['total_qa_pairs']}")
    print(f"   - Training pairs: {summary['training_pairs']}")
    print(f"   - Validation pairs: {summary['validation_pairs']}")
    print(f"   - Conversations: {summary['conversations']}")
    print(f"   - Medical Q&A: {summary['medical_qa']}")
    print(f"   - Emergency Q&A: {summary['emergency_qa']}")
    print(f"\n📁 Files created in {data_dir}:")
    print(f"   - train.jsonl")
    print(f"   - val.jsonl")
    print(f"   - conversations.jsonl")
    print(f"   - data_summary.json")
    
    print("\nNext steps:")
    print("1. Review the generated data")
    print("2. Run: python scripts/fine_tune_model.py")
    print("3. Or use the data with your preferred fine-tuning framework")

if __name__ == "__main__":
    main()
