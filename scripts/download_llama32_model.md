# Download Llama 3.2 3B Model for ctransformers

## Model to Download

**Model**: Llama 3.2 3B Instruct (GGUF format)
**Size**: ~2GB
**Compatible**: ctransformers library (already installed)

## Download Steps

### Option 1: Direct Download (Hugging Face)

1. Go to: https://huggingface.co/TheBloke/Llama-2-7B-Chat-GGUF/tree/main
2. Download: `llama-2-7b-chat.Q4_K_M.gguf` (~4GB)
   - OR for smaller: `llama-2-7b-chat.Q3_K_M.gguf` (~2.8GB)

### Option 2: Use Llama 2 7B (Better Quality)

1. Go to: https://huggingface.co/TheBloke/Llama-2-7B-GGUF
2. Download: `llama-2-7b.Q4_K_M.gguf`

### Option 3: Mistral 7B (Recommended - Best Quality)

1. Go to: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF
2. Download: `mistral-7b-instruct-v0.2.Q4_K_M.gguf` (~4.4GB)
3. Best for SQL and code tasks

## Installation

1. Create models directory:
```bash
mkdir app\models
```

2. Place downloaded model in `app\models\`
   - Example: `app\models\mistral-7b-instruct-v0.2.Q4_K_M.gguf`

3. The module will auto-detect it!

## Recommended Model

**Mistral 7B Instruct** - Best balance of:
- Size (~4.4GB)
- Quality (excellent for SQL/code)
- Speed (fast inference)
- Compatibility (works with ctransformers)

## After Download

1. Place model in `app/models/`
2. Update config (I'll do this)
3. Test: `python scripts/python/test_ai_assistant.py`
4. Done!

---

**Download Link**: https://huggingface.co/TheBloke/Mistral-7B-Instruct-v0.2-GGUF/blob/main/mistral-7b-instruct-v0.2.Q4_K_M.gguf

Click "download" button on that page.