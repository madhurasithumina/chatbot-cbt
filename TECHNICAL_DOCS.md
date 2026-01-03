# CBT Mental Health Chatbot - Technical Documentation

## System Overview

This is an enterprise-level Cognitive Behavioral Therapy (CBT) chatbot that combines a custom-trained model with GPT-4 to provide mental health support.

### Hybrid AI Architecture

The chatbot uses a **dual-model approach**:

1. **Custom CBT Model (40% weight)**
   - Fine-tuned DialoGPT on mental health conversations
   - Specialized in CBT techniques and therapeutic responses
   - Provides domain-specific knowledge

2. **GPT-4 Model (60% weight)**
   - Provides natural language understanding
   - Ensures empathetic, contextual responses
   - Handles edge cases gracefully

3. **Response Merger**
   - Combines both models intelligently
   - Uses confidence scoring
   - Prevents redundancy with semantic similarity checks

## Component Architecture

### 1. Data Layer (`src/data/`)

**CBTDatasetManager** (`dataset_manager.py`)
- Loads mental health conversation datasets from Hugging Face
- Includes curated CBT examples
- Processes and validates data
- Splits into training/validation sets

**Datasets Used:**
- `Amod/mental_health_counseling_conversations` - Professional counseling dialogues
- `heliosbrahma/mental_health_conversational_data` - Mental health conversations
- Custom CBT examples - Handcrafted therapeutic responses

### 2. Model Layer (`src/models/`)

**CBTModel** (`cbt_model.py`)
- Fine-tuned transformer model (DialoGPT-medium)
- Generates CBT-specific responses
- Calculates confidence scores
- Supports training and inference

**Key Methods:**
```python
generate(message, history) -> (response, confidence)
train(train_dataset, eval_dataset, output_dir)
save(path) / load(path)
```

### 3. Core Engine (`src/core/`)

**HybridResponseGenerator** (`hybrid_generator.py`)
- Orchestrates dual-model generation
- Merges responses based on:
  - Confidence scores
  - Configured weights
  - Semantic similarity
- Manages OpenAI API calls

**Merging Strategy:**
```
IF custom_confidence < 0.3:
    USE GPT response
ELIF custom_confidence >= threshold:
    CREATE hybrid (blend both)
ELSE:
    PREFER GPT with validation
```

**CBTChatbotEngine** (`chatbot_engine.py`)
- Manages conversation sessions
- Maintains conversation history
- Tracks emotional states
- Provides session management API

**Session Management:**
- Creates unique session IDs
- Stores conversation history (last 5 turns for context)
- Tracks timestamps and emotional states
- Provides export functionality

### 4. API Layer (`main.py`)

**FastAPI Application**
- RESTful API endpoints
- CORS middleware
- Error handling
- Health checks

**Endpoints:**
```
POST /session              - Create new session
POST /chat                 - Send message, get response
GET  /session/{id}         - Get session info
GET  /session/{id}/history - Get conversation history
DELETE /session/{id}       - End session
GET  /health              - Health check
```

### 5. Configuration (`config/`)

**Settings** (`config.py`)
- Pydantic-based configuration
- Environment variable support
- Type validation

**Key Configuration:**
```python
openai_api_key: str
custom_model_weight: float = 0.4
gpt_model_weight: float = 0.6
confidence_threshold: float = 0.7
```

## Data Flow

```
1. User Input
   ↓
2. Session Retrieval/Creation
   ↓
3. Context Building (last 5 turns)
   ↓
4. Parallel Generation:
   ├─→ Custom Model → (response_1, confidence)
   └─→ GPT-4 → response_2
   ↓
5. Response Merging
   ├─ Confidence evaluation
   ├─ Semantic similarity check
   └─ Weighted combination
   ↓
6. Response Post-processing
   ↓
7. Session Update
   ↓
8. Return to User
```

## Training Pipeline

**Script:** `scripts/train_model.py`

**Steps:**
1. **Data Loading**
   - Fetch mental health datasets from Hugging Face
   - Add curated CBT examples
   - Validate and clean data

2. **Preprocessing**
   - Format as "User: {context} Therapist: {response}"
   - Tokenize with DialoGPT tokenizer
   - Create training batches

3. **Training**
   - Fine-tune DialoGPT-medium
   - 3 epochs (configurable)
   - Learning rate: 2e-5
   - Batch size: 4 with gradient accumulation
   - FP16 training on GPU

4. **Evaluation**
   - Validation loss tracking
   - Save best model
   - Generate test responses

5. **Model Saving**
   - Save to `data/models/cbt_model/`
   - Includes tokenizer and config

**Training Time:** ~30-60 minutes on GPU, longer on CPU

## Response Generation Details

### Custom Model Generation
```python
1. Build context: "User: X Therapist: Y User: Z Therapist:"
2. Tokenize input
3. Generate with sampling (temperature=0.8, top_p=0.9)
4. Calculate confidence from token probabilities
5. Clean and validate response
```

### GPT-4 Generation
```python
1. Build system prompt (CBT therapist role)
2. Add conversation history (last 5 turns)
3. Call OpenAI API
4. Extract response
5. Handle errors gracefully
```

### Response Merging
```python
1. Check custom model confidence
2. If low (<0.3): Use GPT
3. If high (>=0.7): Blend responses
   - Calculate semantic similarity
   - If similar (>0.85): Choose higher confidence
   - If different: Combine intelligently
4. Return final response
```

## Session Management

**Session Lifecycle:**
```
Create → Active → Inactive → Cleanup
```

**Session State:**
```python
{
    "session_id": "uuid",
    "user_id": "optional",
    "conversation_history": [
        {"user": "...", "assistant": "...", "timestamp": "..."}
    ],
    "context": {},
    "created_at": "timestamp",
    "last_active": "timestamp"
}
```

**Memory Management:**
- In-memory storage (current implementation)
- Ready for Redis/Database integration
- Configurable history length (default: 5 turns)

## Error Handling

### Model Errors
- Fallback to base model if trained model unavailable
- Graceful degradation if custom model fails
- Default therapeutic responses as last resort

### API Errors
- OpenAI rate limiting handled
- Timeout handling
- Error responses logged
- User-friendly error messages

### Session Errors
- Auto-create session if not found
- Session timeout handling (planned)
- Concurrent request handling

## Security Considerations

### Current Implementation
- API key in environment variables
- CORS enabled (configure for production)
- Input validation with Pydantic
- No authentication (to be added)

### Production Recommendations
1. **Authentication:**
   - JWT tokens
   - OAuth2 integration
   - User management

2. **Data Privacy:**
   - Encrypt conversations at rest
   - Secure API keys in secrets manager
   - GDPR compliance measures

3. **Rate Limiting:**
   - Per-user rate limits
   - API quota management
   - DDoS protection

4. **Input Sanitization:**
   - XSS prevention
   - SQL injection prevention (when DB added)
   - Input length limits

## Performance Optimization

### Current Performance
- Response time: 2-5 seconds (GPT-4 dependent)
- Concurrent sessions: Unlimited (memory permitting)
- Throughput: ~10-20 req/sec

### Optimization Strategies
1. **Caching:**
   - Cache common responses
   - Vector similarity search for retrieval
   - Redis for session storage

2. **Model Optimization:**
   - Quantization for faster inference
   - Smaller model variants for speed
   - Batch processing

3. **Async Processing:**
   - Async API calls
   - Background model loading
   - Queue-based processing

## Monitoring & Logging

### Current Logging
- Python logging module
- Info/Error level logging
- File output: `logs/chatbot.log`

### Metrics to Track
- Response times
- Model confidence scores
- Error rates
- User satisfaction
- Session duration
- Conversation length

### Recommended Tools
- Prometheus for metrics
- Grafana for visualization
- ELK stack for log analysis
- Sentry for error tracking

## Deployment

### Local Development
```powershell
python main.py  # API server
python console_chat.py  # Console interface
```

### Production Deployment

**Docker:**
```dockerfile
FROM python:3.10
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Cloud Options:**
- AWS: EC2, ECS, Lambda
- Azure: App Service, Container Instances
- GCP: Cloud Run, Compute Engine
- Heroku, Railway, Render

## Future Enhancements

### Phase 1 (Near-term)
- [ ] User authentication system
- [ ] Database integration (PostgreSQL)
- [ ] Session persistence
- [ ] Rate limiting

### Phase 2 (Medium-term)
- [ ] Social media integration APIs
- [ ] Multi-language support
- [ ] Voice interface
- [ ] Mobile app integration

### Phase 3 (Long-term)
- [ ] Advanced emotion detection
- [ ] Personalized treatment plans
- [ ] Analytics dashboard
- [ ] Crisis detection and intervention

## Testing

### Unit Tests
```powershell
pytest tests/test_chatbot.py -v
```

### Integration Tests
```powershell
python scripts/test_system.py
```

### API Tests
```powershell
# Start server
python main.py

# Test with curl or Postman
curl http://localhost:8000/health
```

## Troubleshooting

### Common Issues

**1. OpenAI API Error**
- Check API key in `.env`
- Verify account credits
- Check rate limits

**2. Model Not Found**
- Run training: `python scripts/train_model.py`
- Or download pre-trained model

**3. Memory Issues**
- Reduce batch size in training
- Limit conversation history length
- Use smaller model variant

**4. Slow Response**
- Check internet connection (GPT-4)
- Optimize model size
- Consider caching

## Contributing

### Code Style
- PEP 8 compliance
- Type hints where applicable
- Docstrings for all functions
- Comments for complex logic

### Pull Request Process
1. Fork repository
2. Create feature branch
3. Write tests
4. Update documentation
5. Submit PR

## License

MIT License - see LICENSE file

## Contact & Support

For technical support or questions:
- Check documentation
- Review logs
- Open GitHub issue
- Contact development team
