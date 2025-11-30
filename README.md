# 🤖 SQL Data Analyst Agent

> **AI-Powered Natural Language to SQL with Multi-Database Support**

A production-grade AI agent that converts natural language questions into SQL queries, executes them across multiple database types, visualizes results intelligently, and provides AI-generated insights.

## ✨ Key Features

- 🗣️ **Natural Language Queries**: Ask questions in plain English
- 🗄️ **Multi-Database Support**: SQLite, MySQL, PostgreSQL, SQL Server, Oracle
- 📤 **File Upload**: CSV, Excel, SQLite files (auto-converted)
- 🔄 **Auto Error Recovery**: 3-attempt repair loop with LLM
- 📊 **Smart Visualizations**: Auto-detects chart types (bar, scatter, pie, time series)
- 🧠 **RAG-Enhanced**: Semantic search over database schema
- 💡 **AI Insights**: LLM-generated analysis of results
- 📥 **Export Options**: Download CSV or PDF reports
- 🎨 **Professional UI**: Clean, gradient design with tabs

## 🏗️ Architecture

This project follows a clean, modular architecture designed for scalability and maintainability:

```
Data_analyst_agent/
├── config/              # Configuration management
│   └── settings.py      # Environment variables and app config
├── database/            # Database layer
│   ├── db_setup.py      # SQLite schema and data initialization
│   └── db_manager.py    # Database connection and query execution
├── rag/                 # RAG (Retrieval-Augmented Generation) layer
│   ├── schema_loader.py # Database schema extraction
│   └── vector_store.py  # Chroma vector DB for semantic search
├── agent/               # Agent layer
│   ├── sql_agent.py     # LangChain agent with tools
│   ├── tools.py         # Agent tools (SQL generation, execution)
│   └── error_handler.py # SQL error repair loop
├── ui/                  # Frontend layer
│   ├── app.py           # Streamlit main application
│   ├── components.py    # Reusable UI components
│   └── visualizer.py    # Auto chart generation
├── data/                # Data storage
│   ├── sales_analytics.db  # SQLite database (generated)
│   └── chroma_db/       # Vector DB persistence (generated)
├── .env.example         # Environment variables template
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

## 🚀 Tech Stack

- **Backend**: Python 3.13
- **Agentic Framework**: LangChain (agent with tools)
- **LLM**: Groq (llama-3.3-70b-versatile) - FREE tier with 14,400 requests/day!
- **Embeddings**: Simple SHA-384 based embeddings (no external API needed)
- **RAG**: Chroma vector database with per-session isolation
- **Databases**: 
  - SQLite (embedded)
  - MySQL
  - PostgreSQL
  - SQL Server
  - Oracle
- **Frontend**: Streamlit (gradient design, tabs, responsive)
- **Visualization**: Plotly for interactive charts (auto-detection)
- **Export**: CSV and PDF generation (ReportLab)

## 📊 Database Schema

The project includes a sample sales analytics database with:

- **customers**: Customer information (id, name, email, country, segment)
- **products**: Product catalog (id, name, category, price)
- **orders**: Order transactions (id, customer_id, order_date, status, total_amount)
- **order_items**: Line items (id, order_id, product_id, quantity, unit_price)

## 🎯 Core Features

### Natural Language Processing
- ✅ Convert questions to SQL using Groq llama-3.3-70b
- ✅ Context-aware query generation with RAG
- ✅ Dynamic example questions based on actual schema
- ✅ Identifies ID, percentage, and score columns intelligently

### Database Operations
- ✅ Multi-database support (SQLite, MySQL, PostgreSQL, SQL Server, Oracle)
- ✅ File upload (CSV, Excel, SQLite) with auto-conversion
- ✅ Connection string support for remote databases
- ✅ Automatic schema discovery and indexing
- ✅ Per-session isolation for multi-user support
- ✅ Table name sanitization (handles special characters)

### Query Execution
- ✅ Safe SQL execution with validation
- ✅ Automatic error detection and repair (3 attempts)
- ✅ Schema-aware error fixing with LLM
- ✅ Handles syntax errors, missing columns, type mismatches

### Visualization
- ✅ Auto-detects appropriate chart types:
  - Time series data → Line charts with area fill
  - Categorical + Numeric → Bar charts (top 15)
  - Few categories → Pie/donut charts
  - Two numeric columns → Scatter plots with trendlines
- ✅ Smart sampling for large datasets (500 points)
- ✅ Interactive Plotly charts (zoom, hover, pan)
- ✅ Key metrics with range display
- ✅ Handles ID columns separately (no "highest ID" metrics)

### Insights & Analysis
- ✅ AI-generated insights from query results
- ✅ SQL query explanation
- ✅ Query optimization suggestions
- ✅ Performance analysis

### User Experience
- ✅ Clean gradient UI (#667eea to #764ba2)
- ✅ Tab-based results (Visualization, Insights, Data, SQL, Analysis)
- ✅ Connection info header with visible colors
- ✅ Persistent query input (results don't disappear)
- ✅ Copy SQL button (JavaScript, no reload)
- ✅ Download CSV and PDF reports
- ✅ Previous results remain visible
- ✅ Real-time feedback on every action

### Documentation
- ✅ 18 comprehensive markdown files
- ✅ Architecture documentation
- ✅ Setup guides and troubleshooting
- ✅ Visual guide with screenshots
- ✅ Multi-database guide

## 🛠️ Setup Instructions

### 1. Clone and Navigate
```bash
cd Data_analyst_agent
```

### 2. Create Virtual Environment
```bash
python -m venv venv
# Windows
.\venv\Scripts\activate
# Linux/Mac
source venv/bin/activate
```

### 3. Install Dependencies ✅
```bash
pip install -r requirements.txt
```
**Status**: ✅ Already completed! All packages including `langchain-groq` and `sentence-transformers` are installed.

### 4. Configure Environment ⚠️
```bash
# The .env file is already set up, you just need to add your API key
# Edit .env and add your Groq API key (get it from https://console.groq.com/keys)
# GROQ_API_KEY=gsk-your-actual-key-here
```
**Status**: ⚠️ **ACTION REQUIRED** - Get your free Groq API key and add it to `.env`

See **GROQ_SETUP.md** for detailed instructions on getting your API key.

### 5. Initialize Database & Vector Store
```powershell
python setup.py
```

This will:
- Create the SQLite database with the sales analytics schema
- Populate it with sample data (100+ records)
- Initialize the Chroma vector store with schema embeddings (using free HuggingFace model)

**Status**: ⏳ Ready to run after adding API key

### 6. Run the Application
```powershell
streamlit run ui/app.py
```

The app will open in your browser at `http://localhost:8501`

**Status**: ⏳ Ready to launch after setup

## 💡 Usage Examples

### Quick Start Queries
```
"Show me the first 10 rows"
"How many records are in the table?"
"What columns are available?"
```

### Analytics Queries
```
"Top 5 students by attendance percentage"
"Show total sales by product category"
"What is the average test score by class?"
"Compare attendance and test scores"
```

### Advanced Queries
```
"Which students have attendance above 80% and test scores below average?"
"Show correlation between attendance and final exam scores"
"Find all customers who placed orders in the last 30 days but never returned"
"What products generate the most revenue per category?"
```

### Multi-Table Queries
```
"Show customer names with their total order value"
"List products that have never been ordered"
"Which category has the highest profit margin?"
```

### Time-Based Queries
```
"Show sales trends by month for 2024"
"What day of the week has the most orders?"
"Compare Q1 vs Q4 revenue"
```

The agent automatically:
- Determines which tables to query
- Writes the SQL with JOINs if needed
- Executes and fixes any errors
- Generates appropriate visualizations
- Provides AI insights

## 🔧 Extending the System

### Adding a New Database

1. Update `database/db_setup.py` with your schema
2. Run the setup script to create tables and data
3. The RAG layer will automatically index the new schema

### Switching LLM Provider

1. Update `config/settings.py` with new provider credentials
2. Modify `agent/sql_agent.py` to use the new LLM client
3. Update tool implementations if needed

### Adding Custom Tools

1. Create new tool functions in `agent/tools.py`
2. Register them in the agent initialization
3. Update the system prompt if needed

## 🏛️ Design Principles

- **Separation of Concerns**: Each module has a single, well-defined responsibility
- **Type Safety**: Comprehensive type hints throughout the codebase
- **Documentation**: Detailed docstrings for all functions and classes
- **Error Handling**: Robust error handling with informative messages
- **Extensibility**: Easy to add new databases, tools, or LLM providers
- **Production-Ready**: Configuration management, logging, and best practices

## 📝 Project Structure Details

### Config Layer
Centralizes all configuration management, environment variables, and application settings.

### Database Layer
Handles all database operations including connection management, schema creation, and query execution.

### RAG Layer
Implements semantic search over database schema using Chroma vector store to provide context to the LLM.

### Agent Layer
Contains the LangChain agent with tools for SQL generation, execution, and error repair.

### UI Layer
Streamlit-based frontend with components for query input, results display, visualization, and insights.

## 🤝 Contributing

This is a demonstration project built for the MYAIGURU AI Engineering assignment. For production use, consider:

- Adding authentication and authorization
- Implementing query result caching
- Adding more visualization types
- Supporting multiple databases simultaneously
- Adding query history and bookmarking

## 📄 License

MIT License - Feel free to use this project as a template for your own applications.

## 👨‍💻 Author

Built as part of the MYAIGURU AI Engineering Build Round (November 2025)
