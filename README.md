# Medical Chatbot - AI-Powered Healthcare Assistant

A comprehensive medical chatbot with multimodal RAG capabilities, built for hackathon purposes. This system provides intelligent medical assistance with text, audio, and image inputs, featuring emergency detection, confidence scoring, and multilingual support.

## 🌟 Features

- **Multimodal Input Support**: Text, voice, and image inputs
- **Advanced RAG System**: Semantic + keyword hybrid search
- **Emergency Detection**: Automatic identification of medical emergencies
- **Confidence Scoring**: Transparent confidence levels for responses
- **Emotion Analysis**: Detect user emotional state for better support
- **Multilingual Support**: 45+ languages supported
- **Speech-to-Text**: Powered by OpenAI Whisper
- **Text-to-Speech**: ElevenLabs integration
- **Fine-tuning Capable**: Custom medical domain adaptation
- **Citation Sources**: Transparent source references
- **Memory Integration**: MCP-based conversation memory
- **Modern UI**: Human-like, responsive interface

## 🏗️ Architecture

```
medical_chatbot/
├── api/                    # FastAPI backend
├── frontend/              # React frontend
├── src/                   # Core application code
│   ├── models/           # ML models (LLM, embeddings)
│   ├── rag/              # RAG system components
│   ├── multimodal/       # Text, audio, image processors
│   ├── analysis/         # Confidence, emotion, emergency
│   ├── database/         # Pinecone & MongoDB managers
│   ├── audio/            # Whisper STT & ElevenLabs TTS
│   └── translation/      # Multilingual support
├── config/               # Configuration files
├── scripts/              # Utility scripts
├── docker/               # Docker configuration
└── data/                 # Data storage
```

## 🚀 Quick Start

### Prerequisites

- Python 3.9+
- Node.js 18+
- Docker & Docker Compose (optional)
- API Keys:
  - OpenAI API Key
  - Google Gemini API Key
  - Pinecone API Key
  - ElevenLabs API Key
  - MongoDB URI

### Installation

1. **Clone the repository**
```bash
git clone <repository-url>
cd medical_chatbot
```

2. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

4. **Install frontend dependencies**
```bash
cd frontend
npm install
cd ..
```

5. **Set up databases**
```bash
python scripts/setup_databases.py
```

6. **Ingest medical data**
```bash
python scripts/ingest_medical_data.py
```

### Running the Application

**Option 1: Local Development**

Start the API server:
```bash
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

Start the frontend:
```bash
cd frontend
npm start
```

Access the application at `http://localhost:3000`

**Option 2: Docker**

```bash
cd docker
docker-compose up -d
```

Access the application at `http://localhost`

## 📊 Testing

Test the entire pipeline:
```bash
python scripts/test_pipeline.py
```

## 🎯 Usage

### Text Input
1. Select "Text" mode
2. Type your medical question
3. Receive AI-powered response with confidence score

### Voice Input
1. Select "Voice" mode
2. Click microphone to record
3. Speak your medical question
4. Automatic transcription and response

### Image Input
1. Select "Image" mode
2. Upload medical image (X-ray, skin condition, etc.)
3. Receive AI analysis with body part detection

## ⚙️ Configuration

### API Keys Configuration

Edit `.env` file:

```env
# OpenAI/Gemini
OPENAI_API_KEY=your_openai_key
GEMINI_API_KEY=your_gemini_key

# Pinecone
PINECONE_API_KEY=your_pinecone_key
PINECONE_ENV=your_pinecone_env
PINECONE_INDEX_NAME=medical-chatbot

# MongoDB
MONGO_URI=mongodb://localhost:27017/medical_chatbot
MONGO_DATABASE=medical_chatbot
MONGO_COLLECTION=conversations

# ElevenLabs
ELEVENLABS_API_KEY=your_elevenlabs_key

# Application
DEBUG=True
USE_CUDA=0
SECRET_KEY=your_secret_key
```

## 🔧 Advanced Features

### Fine-tuning

Prepare training data:
```bash
python scripts/prepare_fine_tuning_data.py
```

Fine-tune the model:
```bash
python scripts/fine_tune_model.py
```

### Custom Dataset Ingestion

Ingest your own medical dataset:
```bash
python scripts/ingest_medical_data.py path/to/your/data.json
```

Supported formats: JSON, JSONL, CSV, TXT

## 🛡️ Safety Features

- **Emergency Detection**: Automatic identification of critical conditions
- **Low Confidence Warnings**: Clear indication when AI is uncertain
- **Professional Disclaimer**: Always recommends consulting healthcare professionals
- **Citation Sources**: Transparent reference to medical knowledge base

## 🌍 Multilingual Support

Supports 45+ languages including:
- English, Spanish, French, German, Italian
- Portuguese, Russian, Japanese, Korean, Chinese
- Arabic, Hindi, Thai, Vietnamese, Turkish
- And many more...

## 📈 Monitoring

Access monitoring dashboards:
- Prometheus: `http://localhost:9090`
- Grafana: `http://localhost:3000` (default: admin/admin)

## 🤝 Contributing

This is a hackathon project. Contributions, issues, and feature requests are welcome!

## ⚠️ Disclaimer

**IMPORTANT**: This chatbot is for educational and informational purposes only. It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always seek the advice of qualified healthcare providers with questions regarding medical conditions.

## 📝 License

This project is created for hackathon purposes.

## 🙏 Acknowledgments

- OpenAI for GPT models and Whisper
- Google for Gemini AI
- Pinecone for vector database
- MongoDB for document storage
- ElevenLabs for text-to-speech
- Hugging Face for Sentence Transformers

## 📞 Support

For questions or issues, please open an issue in the repository.

---

**Built with ❤️ for the hackathon**
