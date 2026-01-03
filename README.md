# CBT Mental Health Chatbot

An enterprise-level Cognitive Behavioral Therapy (CBT) chatbot combining custom-trained models with GPT for mental health support.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        User Interface                         │
└───────────────────────────┬───────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────┐
│                      API Layer (FastAPI)                       │
│  - Authentication  - Rate Limiting  - Session Management      │
└───────────────────────────┬───────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────┐
│                   Chatbot Engine (Core)                        │
│  ┌─────────────────────────────────────────────────────────┐  │
│  │           Hybrid Response Generator                      │  │
│  │  ┌──────────────────┐      ┌──────────────────┐        │  │
│  │  │  Custom CBT Model │ ───► │  Response Merger │        │  │
│  │  └──────────────────┘      └──────────────────┘        │  │
│  │  ┌──────────────────┐              │                    │  │
│  │  │   GPT-4 Model    │ ─────────────┘                    │  │
│  │  └──────────────────┘                                    │  │
│  └─────────────────────────────────────────────────────────┘  │
└───────────────────────────┬───────────────────────────────────┘
                            │
┌───────────────────────────▼───────────────────────────────────┐
│                    Data & Model Layer                          │
│  - Vector DB  - Session Store  - Training Pipeline            │
└─────────────────────────────────────────────────────────────────┘
```

## Features

- **Hybrid AI Response**: Combines custom-trained CBT model with GPT for optimal responses
- **Enterprise-Grade**: Scalable architecture with proper separation of concerns
- **Session Management**: Maintains conversation context across interactions
- **Training Pipeline**: Automated model training and evaluation
- **Mental Health Focus**: Specialized in CBT techniques and mental health support
- **Extensible**: Ready for social media integration (future feature)

## Project Structure

```
chatbot-cbt/
├── src/
│   ├── api/              # API endpoints and routes
│   ├── core/             # Core chatbot logic
│   ├── models/           # ML models and training
│   ├── data/             # Data processing and management
│   ├── services/         # Business logic services
│   └── utils/            # Utility functions
├── data/
│   ├── raw/              # Raw datasets
│   ├── processed/        # Processed training data
│   └── models/           # Trained model files
├── config/               # Configuration files
├── tests/                # Unit and integration tests
└── scripts/              # Training and deployment scripts
```

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Configure environment:
```bash
cp .env.example .env
# Edit .env with your API keys
```

3. Train the model:
```bash
python scripts/train_model.py
```

4. Run the chatbot:
```bash
python main.py
```

## Dataset

Using curated mental health and CBT conversation datasets for training.

## Technologies

- **Python 3.10+**
- **FastAPI**: API framework
- **PyTorch/Transformers**: Model training
- **OpenAI GPT**: Advanced language understanding
- **Redis**: Session management (optional)
- **SQLAlchemy**: Data persistence (optional)
- **ChromaDB**: Vector database (optional, requires C++ build tools)

## License

MIT License
