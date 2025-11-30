# Groq API Setup Guide

## Overview
This project has been configured to use **Groq** (free tier) instead of OpenAI due to its generous free API limits and fast inference.

## Why Groq?
- ✅ **Free Tier**: 14,400 requests per day (vs OpenAI's paid-only model)
- ✅ **Fast**: Groq's LPU (Language Processing Unit) delivers ultra-fast inference
- ✅ **Compatible**: Works seamlessly with LangChain
- ✅ **Model**: Using `llama-3.3-70b-versatile` (70B parameter model)

## Setup Steps

### Step 1: Get Your Groq API Key

1. Go to: **https://console.groq.com/keys**
2. Sign up or log in (free account)
3. Click "Create API Key"
4. Copy your API key (starts with `gsk_...`)

### Step 2: Configure Your Environment

Open the `.env` file in the project root and update it:

```env
# LLM Provider Configuration
LLM_PROVIDER=groq
GROQ_API_KEY=gsk_your_actual_api_key_here

# Model Configuration
LLM_MODEL=llama-3.3-70b-versatile
LLM_TEMPERATURE=0.0

# Database
DATABASE_PATH=./data/sales_analytics.db

# Chroma Vector Store
CHROMA_PERSIST_DIR=./data/chroma_db
CHROMA_COLLECTION_NAME=sql_schema
```

**Important**: Replace `gsk_your_actual_api_key_here` with your actual Groq API key!

### Step 3: Verify Installation

Check that all dependencies are installed:

```powershell
pip list | Select-String -Pattern "groq|sentence"
```

You should see:
- `groq` (0.36.0 or higher)
- `langchain-groq` (1.1.0 or higher)
- `sentence-transformers` (5.1.2 or higher)

If any are missing, run:
```powershell
pip install langchain-groq sentence-transformers
```

### Step 4: Initialize the Database and Vector Store

Run the setup script:

```powershell
python setup.py
```

This will:
1. ✅ Create the SQLite database with sample sales data
2. ✅ Initialize the Chroma vector store with schema embeddings (using free HuggingFace embeddings)

Expected output:
```
🚀 Starting SQL Data Analyst Agent setup...

📊 Setting up database...
✅ Database created successfully at: D:\Data_analyst_agent\data\sales_analytics.db

🔍 Initializing vector store...
✅ Vector store initialized with X documents

✅ Setup completed successfully!
```

### Step 5: Launch the Application

Start the Streamlit app:

```powershell
streamlit run ui/app.py
```

The app will open in your browser at: **http://localhost:8501**

## What Changed from OpenAI?

### Code Changes Made:
1. **LLM Provider**: `ChatOpenAI` → `ChatGroq`
2. **Embeddings**: `OpenAIEmbeddings` → `HuggingFaceEmbeddings` (free, local)
3. **Configuration**: Added `GROQ_API_KEY` and `LLM_PROVIDER` settings
4. **Dependencies**: Added `langchain-groq` and `sentence-transformers`

### Files Modified:
- `.env` - Added Groq configuration
- `config/settings.py` - Added Groq API key validation
- `agent/sql_agent.py` - Changed to ChatGroq
- `agent/error_handler.py` - Changed to ChatGroq
- `rag/vector_store.py` - Changed to HuggingFaceEmbeddings
- `requirements.txt` - Added new dependencies

## Troubleshooting

### Issue: "Import 'langchain_groq' could not be resolved"
**Solution**: VS Code type checking may lag. The package is installed. Either:
- Restart VS Code, or
- Run the code - it will work despite the editor warning

### Issue: "Invalid API key" or authentication errors
**Solution**: 
1. Verify your `.env` file has the correct Groq API key
2. Make sure the key starts with `gsk_`
3. Check at https://console.groq.com/keys that the key is active

### Issue: Vector store initialization fails
**Solution**: 
1. First time will download HuggingFace model (~120MB) - this is normal
2. Make sure you have internet connection
3. The model is cached locally after first download

### Issue: Database not found
**Solution**: 
1. Run `python setup.py` to create the database
2. Check that `data/sales_analytics.db` exists

## Testing Your Setup

Try these example queries in the Streamlit app:

1. **Simple query**: "Show me all customers"
2. **Aggregation**: "What are the top 5 products by total revenue?"
3. **Join query**: "Show me orders from January 2024 with customer names"
4. **Complex**: "Which customers have spent more than $1000 total?"

## API Rate Limits

**Groq Free Tier**:
- 14,400 requests per day
- 30 requests per minute
- More than enough for development and testing!

## Next Steps

1. ✅ Get your Groq API key
2. ✅ Update `.env` file
3. ✅ Run `python setup.py`
4. ✅ Launch with `streamlit run ui/app.py`
5. 🎉 Start querying your database with natural language!

---

## Additional Resources

- Groq Console: https://console.groq.com/
- Groq Documentation: https://console.groq.com/docs
- LangChain Groq Integration: https://python.langchain.com/docs/integrations/chat/groq
- Project Documentation: See `docs/` folder
