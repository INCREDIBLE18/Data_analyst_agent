# 🚀 Quick Start Guide - SQL Data Analyst Agent

## 🎉 NEW: Multi-Database Support!

Now supports **ANY DATABASE**! Upload files or connect to remote databases.

This is a production-grade SQL Data Analyst Agent built with:
- **LangChain** for agentic workflows
- **Groq (llama-3.3-70b)** for natural language understanding (FREE!)
- **Chroma** vector DB for schema RAG
- **SQLite, MySQL, PostgreSQL** support
- **Dynamic schema discovery** for any database
- **Streamlit** for the UI

### Prerequisites
✅ Python 3.13 - Already have it!
✅ Most dependencies - Already installed!
📦 NEW dependencies - See below

## Setup Steps

### 1. Install NEW Dependencies (1 minute)
```powershell
pip install sqlalchemy pymysql psycopg2-binary langchain-community
```

### 2. Get Groq API Key (1 minute)
1. Visit: **https://console.groq.com/keys**
2. Sign up for free account
3. Click "Create API Key"
4. Copy the key (starts with `gsk_...`)

### 3. Configure Environment (30 seconds)
Open `.env` file and update:
```env
GROQ_API_KEY=gsk_your_actual_key_here
```

### 4. Launch the App
```powershell
streamlit run ui/app.py
```

The app will open at http://localhost:8501

## 🆕 Using Multi-Database Features

### Quick Start: Upload Sample CSV
1. **Run the app** (see step 4 above)
2. **Click "Upload Database File" tab**
3. **Drag `sample_data.csv`** (included in project)
4. **Click "Connect"** - System auto-converts to SQLite
5. **Click "Start Analyzing"**
6. **Ask**: "What's the total revenue?"

### Upload Your Own Database
1. Click "Upload Database File" tab
2. Upload .db, .sqlite, .csv file
3. View discovered schema
4. Click "Start Analyzing"
5. Query naturally!

### Connect to Remote Database
1. Click "Connection String" tab
2. Select database type (MySQL, PostgreSQL, etc.)
3. Enter connection string:
   - MySQL: `mysql+pymysql://user:pass@host:3306/db`
   - PostgreSQL: `postgresql://user:pass@host:5432/db`
4. Click "Connect"
5. Start querying!

## Example Queries

Try these natural language questions:
- "Show me total sales by product category"
- "What are the top 5 customers by revenue?"
- "How many orders were placed each month in 2024?"
- "Which products have never been ordered?"
- "What is the average order value by customer segment?"

## Architecture

```
├── config/          # Configuration and settings
├── database/        # Database setup and management
├── rag/            # Vector store and schema RAG
├── agent/          # LangChain agent with tools
├── ui/             # Streamlit frontend
└── data/           # Database and vector store files
```

See README.md for complete documentation.
