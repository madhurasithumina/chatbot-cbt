# Network Issues During Training

## Problem
The training script is timing out while downloading the DialoGPT-medium model (863MB) from Hugging Face.

## Quick Solutions

### Option 1: Use Smaller Model (Faster Download)
```powershell
# Edit scripts/train_model.py and change line 80
MODEL_NAME = "microsoft/DialoGPT-small"  # Instead of DialoGPT-medium
```

### Option 2: Try Again Later
Your internet may be slow or Hugging Face servers may be busy. The model download resumes where it left off.

```powershell
python scripts\train_model.py
```

### Option 3: Skip Training (Use Base Model)
The chatbot works without training using the base GPT-4 model:

```powershell
# Just run the chatbot directly
python console_chat.py
```

It will use GPT-4 (60%) + untrained base model (40%).

### Option 4: Download Model Manually
Download the model manually and place in cache:

1. Visit: https://huggingface.co/microsoft/DialoGPT-medium/tree/main
2. Download `pytorch_model.bin` (863 MB)
3. Place in: `C:\Users\User\.cache\huggingface\hub\models--microsoft--DialoGPT-medium\`

## What Works Now

✅ Dataset loading is fixed - loaded 18 conversations successfully
✅ Train/validation split working
✅ Only issue is slow network download

## Recommended: Use Chatbot Without Training

Since training takes time and requires large downloads, you can use the chatbot immediately:

```powershell
.\venv\Scripts\Activate.ps1

# Make sure .env has your OPENAI_API_KEY
notepad .env

# Run chatbot (works without training)
python console_chat.py
```

The chatbot will use:
- GPT-4 for intelligent responses (60%)
- Base DialoGPT model for CBT structure (40%)

You can train later when you have better internet or more time!
