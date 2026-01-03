# CBT Chatbot - Quick Start Guide

## Setup Instructions

### 1. Install Dependencies

```powershell
# Create virtual environment (recommended)
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```powershell
# Copy example environment file
copy .env.example .env

# Edit .env file and add your OpenAI API key
notepad .env
```

**Important**: Set your `OPENAI_API_KEY` in the `.env` file:
```
OPENAI_API_KEY=sk-your-key-here
SECRET_KEY=your-secret-key-here
```

### 3. Train the Model (First Time Setup)

```powershell
# Train the custom CBT model on mental health datasets
python scripts\train_model.py
```

This will:
- Download mental health conversation datasets
- Process and prepare the data
- Fine-tune a DialoGPT model on CBT conversations
- Save the trained model to `data/models/cbt_model/`

**Note**: Training requires internet connection and may take 30-60 minutes depending on your hardware.

### 4. Test the System

```powershell
# Run quick tests to verify setup
python scripts\test_system.py
```

### 5. Run the Chatbot

#### Option A: Console Interface (Simple)

```powershell
python console_chat.py
```

This provides an interactive command-line interface.

#### Option B: API Server (Full Features)

```powershell
python main.py
```

Then access:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

## Usage Examples

### Console Chat

```
💭 You: I'm feeling really anxious about my presentation tomorrow.
🤖 Bot: It sounds like you're experiencing anticipatory anxiety...
```

Commands:
- `help` - Show available commands
- `history` - View conversation history
- `clear` - Start new session
- `quit` - Exit

### API Usage

#### Create Session
```bash
curl -X POST http://localhost:8000/session
```

#### Send Message
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "session_id": "your-session-id",
    "message": "I am feeling anxious"
  }'
```

#### Get History
```bash
curl http://localhost:8000/session/{session_id}/history
```

## Architecture Overview

```
User Input
    ↓
API Layer (FastAPI)
    ↓
Chatbot Engine
    ↓
Hybrid Response Generator
    ├─→ Custom CBT Model (40%)
    └─→ GPT-4 Model (60%)
    ↓
Merged Response
```

## Key Features

✅ **Hybrid AI**: Combines custom-trained CBT model with GPT-4  
✅ **Mental Health Focused**: Trained on real therapy conversations  
✅ **Session Management**: Maintains conversation context  
✅ **Enterprise Architecture**: Scalable, production-ready design  
✅ **RESTful API**: Easy integration with any frontend  
✅ **Extensible**: Ready for social media integration

## Troubleshooting

### ModuleNotFoundError
```powershell
# Make sure you're in the virtual environment
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### OpenAI API Error
- Verify your API key in `.env`
- Check your OpenAI account has credits
- Ensure internet connection

### Model Not Found
- Run training first: `python scripts\train_model.py`
- Or the system will use base model (works but less specialized)

### CUDA/GPU Errors
- System works on CPU (slower training)
- For GPU support, install PyTorch with CUDA: https://pytorch.org/

## Development

### Project Structure
```
chatbot-cbt/
├── src/
│   ├── core/           # Chatbot engine & hybrid generator
│   ├── models/         # Custom CBT model
│   ├── data/           # Dataset management
│   └── api/            # API routes (in main.py)
├── data/
│   ├── raw/            # Raw datasets
│   ├── processed/      # Processed data
│   └── models/         # Trained models
├── config/             # Configuration
├── scripts/            # Training & testing scripts
├── main.py             # API server
└── console_chat.py     # Console interface
```

### Adding Custom Responses

Edit [src/data/dataset_manager.py](src/data/dataset_manager.py) and add to `_get_cbt_examples()` method.

### Adjusting Model Weights

In `.env` file:
```
CUSTOM_MODEL_WEIGHT=0.4    # Custom CBT model influence
GPT_MODEL_WEIGHT=0.6       # GPT-4 influence
CONFIDENCE_THRESHOLD=0.7   # Threshold for hybrid blending
```

## Next Steps

1. **Social Media Integration**: API is ready for frontend integration
2. **Database**: Configure PostgreSQL for production persistence
3. **Authentication**: Implement user authentication system
4. **Monitoring**: Add logging and metrics collection
5. **Deployment**: Deploy to cloud (AWS, Azure, GCP)

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review the API documentation at `/docs`
3. Examine logs in `logs/chatbot.log`

## Important Notes

⚠️ **This is a supportive tool, not a replacement for professional therapy**  
⚠️ **Always encourage users to seek professional help for serious concerns**  
⚠️ **Maintain user privacy and data security in production**
