// MongoDB initialization script

// Switch to the medical_chatbot database
db = db.getSiblingDB('medical_chatbot');

// Create collections
db.createCollection('conversations');
db.createCollection('medical_data');
db.createCollection('user_feedback');
db.createCollection('system_logs');

// Create indexes for better performance
db.conversations.createIndex({ "user_id": 1 });
db.conversations.createIndex({ "session_id": 1 });
db.conversations.createIndex({ "created_at": 1 });
db.conversations.createIndex({ "updated_at": 1 });
db.conversations.createIndex({ "user_id": 1, "updated_at": -1 });

// Text index for message content search
db.conversations.createIndex({ "messages.content": "text" });

// Medical data indexes
db.medical_data.createIndex({ "data_type": 1 });
db.medical_data.createIndex({ "created_at": 1 });
db.medical_data.createIndex({ "metadata.category": 1 });
db.medical_data.createIndex({ "metadata.source": 1 });

// User feedback indexes
db.user_feedback.createIndex({ "conversation_id": 1 });
db.user_feedback.createIndex({ "message_id": 1 });
db.user_feedback.createIndex({ "created_at": 1 });

// System logs indexes
db.system_logs.createIndex({ "timestamp": 1 });
db.system_logs.createIndex({ "level": 1 });
db.system_logs.createIndex({ "component": 1 });

// Insert initial medical data
db.medical_data.insertMany([
    {
        "data_type": "medical_knowledge",
        "content": "Chest pain can be a sign of a heart attack. If you experience severe chest pain, seek immediate medical attention.",
        "metadata": {
            "source": "medical_textbook",
            "category": "cardiology",
            "author": "Dr. Smith",
            "publication_date": "2023-01-01"
        },
        "created_at": new Date(),
        "updated_at": new Date()
    },
    {
        "data_type": "medical_knowledge",
        "content": "Fever is a common symptom of infection. Normal body temperature is around 98.6°F (37°C).",
        "metadata": {
            "source": "medical_guide",
            "category": "general_medicine",
            "author": "Dr. Johnson",
            "publication_date": "2023-02-01"
        },
        "created_at": new Date(),
        "updated_at": new Date()
    },
    {
        "data_type": "medical_knowledge",
        "content": "Headaches can be caused by stress, dehydration, or underlying medical conditions. Severe headaches may require medical evaluation.",
        "metadata": {
            "source": "medical_journal",
            "category": "neurology",
            "author": "Dr. Brown",
            "publication_date": "2023-03-01"
        },
        "created_at": new Date(),
        "updated_at": new Date()
    }
]);

// Create a system user for testing
db.conversations.insertOne({
    "user_id": "system_user",
    "session_id": "initial_session",
    "created_at": new Date(),
    "updated_at": new Date(),
    "messages": [],
    "metadata": {
        "language": "en",
        "total_messages": 0,
        "last_activity": new Date()
    }
});

print("Medical Chatbot database initialized successfully!");
