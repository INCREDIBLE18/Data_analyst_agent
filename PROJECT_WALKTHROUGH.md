# SQL Data Analyst Agent - Project Walkthrough

## Overview

This is an AI-powered SQL Data Analyst Agent that converts natural language questions into SQL queries, executes them across multiple database types, and provides intelligent visualizations and insights. Built for production use with a focus on reliability, user experience, and extensibility.

---

## 1. Architecture

The application follows a **5-layer modular architecture** for clean separation of concerns:

### Layer 1: Configuration Layer
- **Purpose:** Centralized configuration management
- **Components:**
  - Environment variable loading (`.env` file)
  - API key management (Groq API)
  - Application settings (retry attempts, timeouts, etc.)
- **Files:** `config/settings.py`

### Layer 2: Database Layer
- **Purpose:** Data access and schema management
- **Components:**
  - Multi-database connection manager (SQLite, MySQL, PostgreSQL, SQL Server, Oracle)
  - File upload handler (CSV, Excel → SQLite conversion)
  - Automatic schema discovery (tables, columns, types, relationships)
  - Query execution engine
- **Files:** 
  - `database/connection_manager.py`
  - `database/schema_discoverer.py`

### Layer 3: RAG (Retrieval-Augmented Generation) Layer
- **Purpose:** Semantic search over database schema
- **Components:**
  - Schema indexing with simple SHA-384 embeddings (no API needed)
  - Session-based vector stores (Chroma DB)
  - Semantic similarity search for relevant context
  - Top-K context retrieval for LLM
- **Files:**
  - `rag/dynamic_vector_store.py`
  - `rag/schema_loader.py`

### Layer 4: Agent Layer
- **Purpose:** AI orchestration and SQL generation
- **Components:**
  - SQL query generation using Groq LLM (llama-3.3-70b)
  - Query validation and optimization
  - Automatic error detection and repair (up to 3 attempts)
  - AI insight generation
- **Files:**
  - `agent/sql_agent.py`
  - `agent/error_handler.py`
  - `agent/sql_validator.py`

### Layer 5: UI Layer
- **Purpose:** User interface and visualization
- **Components:**
  - Streamlit web interface
  - Interactive Plotly visualizations
  - Multi-tab result display
  - PDF/CSV export functionality
- **Files:**
  - `ui/app.py` (241 lines)
  - `ui/components.py` (1,188 lines)
  - `ui/visualizer.py`

### Data Flow

```
User Question → UI Layer → Agent Layer → RAG Layer → Database Layer
                  ↓           ↓            ↓            ↓
              Display ← Insights ← Context ← Schema ← Query Results
```

**Example Flow:**
1. User asks: "Show top 5 patients with highest symptom count"
2. Agent expands query for better semantic matching
3. RAG retrieves relevant schema (Healthcare table, Symptom_Count column)
4. LLM generates SQL with context
5. Database executes query
6. Visualizer creates appropriate chart
7. Agent generates insights
8. UI displays results in organized tabs

---

## 2. Tech Stack

### Backend
| Technology | Purpose | Why Chosen |
|-----------|---------|------------|
| **Python 3.13** | Core language | Latest features, type hints, performance |
| **LangChain** | Agent orchestration | Industry standard for LLM apps |
| **Groq API** | LLM inference | FREE 14,400 requests/day, fast inference |
| **llama-3.3-70b** | SQL generation | Best balance of accuracy and speed |

### AI & Embeddings
| Technology | Purpose | Why Chosen |
|-----------|---------|------------|
| **SHA-384 Hash** | Simple embeddings | No API calls needed, deterministic |
| **Chroma DB** | Vector storage | Lightweight, embedded, session-based |

### Database
| Technology | Purpose | Why Chosen |
|-----------|---------|------------|
| **SQLAlchemy** | Database ORM | Supports 5+ database types |
| **SQLite** | File upload storage | Zero-config, embedded database |
| **MySQL/PostgreSQL** | Production DBs | Enterprise database support |
| **Pandas** | Data processing | Standard data manipulation library |

### Frontend & Visualization
| Technology | Purpose | Why Chosen |
|-----------|---------|------------|
| **Streamlit** | Web framework | Rapid development, Python-native |
| **Plotly** | Interactive charts | Beautiful, interactive visualizations |
| **ReportLab** | PDF export | Professional report generation |

### Key Advantages:
- ✅ **FREE Tier:** Groq provides 14,400 free requests/day
- ✅ **No External Embedding API:** Simple hash-based embeddings
- ✅ **Multi-Database:** Works with SQLite, MySQL, PostgreSQL, SQL Server, Oracle
- ✅ **Offline Capable:** Core functionality works without internet (except LLM calls)

---

## 3. Agent / RAG Workflow

### Step-by-Step Process

#### Step 1: Query Reception
```python
# User asks: "Show patients with high symptom count"
question = user_input
```

#### Step 2: Query Expansion
```python
# Expand query for better semantic matching
expanded_queries = [
    "patients with most symptoms",
    "highest symptom count patients",
    "severe case patients"
]
```

#### Step 3: RAG Context Retrieval
```python
# Search vector store for relevant schema
schema_context = vectorstore.similarity_search(
    query=expanded_query,
    k=5  # Top 5 most relevant chunks
)

# Returns:
# - Table: Healthcare
# - Columns: Patient_ID, Symptom_Count, Age, Gender, Disease
# - Sample data: Max=7, Min=3, Avg=4.5
```

#### Step 4: SQL Generation with LLM
```python
prompt = f"""You are a SQL expert. Generate a valid SQL query.

Schema Context:
{schema_context}

User Question: {question}

Generate ONLY the SQL query:"""

response = groq_llm.invoke(prompt)
sql_query = extract_sql(response)

# Generated: SELECT Patient_ID, Symptom_Count FROM Healthcare 
#            ORDER BY Symptom_Count DESC LIMIT 5
```

#### Step 5: Query Validation
```python
# Validate query before execution
validation_checks = [
    "✓ Valid SQL syntax",
    "✓ Table exists: Healthcare",
    "✓ Columns exist: Patient_ID, Symptom_Count",
    "✓ No dangerous operations (DROP, DELETE)",
    "✓ Performance acceptable"
]
```

#### Step 6: Execute with Error Recovery
```python
max_attempts = 3
for attempt in range(1, max_attempts + 1):
    df, error = execute_query(sql_query)
    
    if error is None:
        break  # Success!
    
    if attempt < max_attempts:
        # Use LLM to repair the query
        sql_query = llm_repair_query(sql_query, error, schema_context)

# If still fails after 3 attempts, return error to user
```

#### Step 7: Visualization Auto-Detection
```python
# Automatically choose best chart type
if has_time_column(df):
    chart_type = "line"  # Time series
elif has_categorical_and_numeric(df):
    chart_type = "bar"   # Bar chart
elif few_categories(df):
    chart_type = "pie"   # Pie chart
elif two_numeric_columns(df):
    chart_type = "scatter"  # Scatter plot
```

#### Step 8: Insight Generation
```python
prompt = f"""Analyze these query results and provide insights:

Query: {question}
Results: {df.to_string()}

Provide 3-5 key insights:"""

insights = groq_llm.invoke(prompt)

# Generated: "Patient #8 (Bronchitis) shows 6 symptoms at age 25,
#            indicating severe respiratory complications..."
```

#### Step 9: Display Results
```python
# Organize in tabs
tabs = st.tabs(["📊 Visualization", "💡 Insights", "📋 Data", 
                "🔍 SQL", "⚡ Analysis"])

with tabs[0]:
    st.plotly_chart(chart)  # Interactive chart
with tabs[1]:
    st.markdown(insights)   # AI insights
with tabs[2]:
    st.dataframe(df)        # Raw data
with tabs[3]:
    st.code(sql_query)      # SQL with copy button
with tabs[4]:
    st.write(optimization_tips)  # Query analysis
```

### RAG Architecture Details

**Vector Store Structure:**
```
session_vector_stores/
├── session_abc123/
│   ├── chroma.sqlite3      # Chroma DB
│   └── index/              # Vector indices
│       ├── table_healthcare.vec
│       ├── column_patient_id.vec
│       └── sample_data.vec
```

**Schema Document Format:**
```json
{
  "page_content": "Table: Healthcare | Columns: Patient_ID (INTEGER), Age (INTEGER), Gender (TEXT), Symptoms (TEXT), Symptom_Count (INTEGER), Disease (TEXT) | Sample: Patient #1, Age 45, Gender Male, Disease Diabetes, Symptom_Count 7",
  "metadata": {
    "type": "table_schema",
    "table": "Healthcare",
    "columns": 6,
    "rows": 3000
  }
}
```

---

## 4. UI Design

### Design Principles

#### 1. **Professional Gradient Theme**
```python
# Color palette
PRIMARY_GRADIENT = "linear-gradient(135deg, #667eea 0%, #764ba2 100%)"
BACKGROUND = "#e8f4f8"
TEXT = "#1e3a8a"
ACCENT = "#667eea"
```

#### 2. **Progressive Disclosure**
The UI reveals information in stages to avoid overwhelming users:

**Stage 1: Database Connection**
- Upload file OR enter connection string
- Clean, simple interface

**Stage 2: Schema Overview**
- Automatic schema discovery results
- Database statistics (tables, columns, rows)
- Expandable schema viewer

**Stage 3: Query Interface**
- Natural language input with examples
- Quick action buttons for common queries
- Query history in sidebar

**Stage 4: Results Display**
- 5-tab organization (Visualization, Insights, Data, SQL, Analysis)
- Export options (CSV, PDF)

#### 3. **Tab-Based Results Organization**

**Tab 1: 📊 Visualization**
- Interactive Plotly chart (zoom, pan, hover)
- Auto-detected chart type
- Professional styling with gradients

**Tab 2: 💡 Insights**
- AI-generated analysis
- Key findings highlighted
- Business recommendations

**Tab 3: 📋 Data Table**
- Sortable, filterable table
- Pagination for large results
- Column statistics

**Tab 4: 🔍 SQL Query**
- Syntax-highlighted SQL
- Copy-to-clipboard button
- Query explanation

**Tab 5: ⚡ Analysis**
- Query performance metrics
- Optimization suggestions
- Index recommendations

#### 4. **Error Handling UX**
```python
# Friendly error messages
if error_type == "column_not_found":
    st.warning("⚠️ Column not found. Did you mean 'Symptom_Count'?")
    st.info("💡 Tip: Check the Schema tab for available columns")

# Success with repair info
st.success("✅ Query executed successfully after 2 repair attempts")
```

#### 5. **Responsive Layout**
```python
# Sidebar: Always visible
with st.sidebar:
    - Connection status
    - Query history
    - Schema quick reference
    - Settings

# Main: Dynamic content
- Full-width query input
- Grid layout for results
- Adaptive chart sizing
```

### Key UI Components

**File: `ui/components.py`**

1. **`render_connection_interface()`** - Database connection UI
2. **`render_query_input()`** - Natural language input with suggestions
3. **`render_results()`** - Multi-tab result display
4. **`render_sidebar()`** - History, schema, settings
5. **`render_schema_view()`** - Expandable schema tree

**File: `ui/visualizer.py`**

1. **`create_visualization()`** - Auto-chart generation
2. **`_determine_viz_type()`** - Smart chart type detection
3. **`_create_bar_chart()`** - Enhanced bar charts with gradients
4. **`_create_time_series()`** - Time series with range selector

---

## 5. How to Extend the Solution

### Extension 1: Add New Database Types

**Difficulty:** Medium | **Impact:** High

```python
# File: database/connection_manager.py

def create_engine(connection_string: str):
    # Add MongoDB support
    if connection_string.startswith("mongodb://"):
        from pymongo import MongoClient
        return MongoClient(connection_string)
    
    # Add BigQuery support
    elif connection_string.startswith("bigquery://"):
        from google.cloud import bigquery
        return bigquery.Client()
    
    # Existing: SQLAlchemy for SQL databases
    else:
        return sqlalchemy.create_engine(connection_string)
```

**Steps:**
1. Add new connection parser in `connection_manager.py`
2. Implement schema discovery for new DB type
3. Add query execution adapter
4. Update UI connection form with new option
5. Add documentation and examples

---

### Extension 2: Multi-Language Support

**Difficulty:** Easy | **Impact:** Medium

```python
# File: config/i18n.py

translations = {
    "en": {
        "query_placeholder": "Ask your question...",
        "execute_button": "🚀 Analyze",
        "error_no_results": "No results found"
    },
    "es": {
        "query_placeholder": "Haga su pregunta...",
        "execute_button": "🚀 Analizar",
        "error_no_results": "No se encontraron resultados"
    }
}

# File: ui/app.py
language = st.selectbox("Language", ["en", "es", "fr", "de"])
t = translations[language]
st.text_area(t["query_placeholder"])
```

---

### Extension 3: Advanced Visualizations

**Difficulty:** Medium | **Impact:** High

```python
# File: ui/visualizer.py

def create_advanced_viz(df, viz_type):
    if viz_type == "heatmap":
        # Correlation heatmap
        fig = px.imshow(df.corr(), text_auto=True)
    
    elif viz_type == "3d_scatter":
        # 3D scatter plot
        fig = px.scatter_3d(df, x='Age', y='Symptom_Count', 
                           z='Disease_Severity')
    
    elif viz_type == "sunburst":
        # Hierarchical sunburst
        fig = px.sunburst(df, path=['Disease', 'Gender', 'Age_Group'])
    
    elif viz_type == "treemap":
        # Treemap for hierarchical data
        fig = px.treemap(df, path=['Region', 'Hospital', 'Department'])
    
    return fig
```

**Additional Chart Types:**
- Sankey diagrams for flow analysis
- Funnel charts for conversion analysis
- Gantt charts for timeline data
- Network graphs for relationship data
- Geographic maps for location data

---

### Extension 4: Query Caching

**Difficulty:** Easy | **Impact:** High (Performance)

```python
# File: agent/query_cache.py

from functools import lru_cache
import hashlib

class QueryCache:
    def __init__(self, max_size=100):
        self.cache = {}
        self.max_size = max_size
    
    def get_cache_key(self, query: str, db_schema: str) -> str:
        # Create hash from query + schema
        content = f"{query}|{db_schema}"
        return hashlib.sha256(content.encode()).hexdigest()
    
    def get(self, query: str, schema: str):
        key = self.get_cache_key(query, schema)
        return self.cache.get(key)
    
    def set(self, query: str, schema: str, result):
        key = self.get_cache_key(query, schema)
        self.cache[key] = {
            'result': result,
            'timestamp': datetime.now(),
            'ttl': 3600  # 1 hour
        }

# Usage in sql_agent.py
if cached_result := query_cache.get(question, schema):
    return cached_result
```

---

### Extension 5: Natural Language to Visualization

**Difficulty:** Medium | **Impact:** Medium

```python
# File: ui/viz_agent.py

def interpret_viz_request(query: str) -> str:
    """Use LLM to detect visualization intent."""
    
    prompt = f"""User query: {query}

What visualization would be best?
Options: bar, line, pie, scatter, heatmap, table

Return only the chart type:"""
    
    chart_type = llm.invoke(prompt).strip().lower()
    return chart_type

# Usage
query = "show me a trend of sales over time"
viz_type = interpret_viz_request(query)  # Returns: "line"
```

**Enhanced Features:**
- "Show me a pie chart of disease distribution"
- "Plot age vs symptom count as scatter"
- "Give me a heatmap of correlations"

---

### Extension 6: Multi-Query Sessions

**Difficulty:** Hard | **Impact:** High

```python
# File: agent/conversation_memory.py

class ConversationMemory:
    def __init__(self):
        self.history = []
    
    def add_interaction(self, query: str, sql: str, results: pd.DataFrame):
        self.history.append({
            'query': query,
            'sql': sql,
            'results': results,
            'timestamp': datetime.now()
        })
    
    def get_context(self) -> str:
        """Build context from previous queries."""
        context = "Previous queries in this session:\n"
        for i, item in enumerate(self.history[-3:], 1):
            context += f"{i}. Q: {item['query']}\n"
            context += f"   SQL: {item['sql']}\n"
        return context

# Usage
query = "now show me just the female patients"
context = memory.get_context()
# LLM can reference previous query to understand "now"
```

**Enables:**
- "Show me the top 10 patients by symptom count"
- "Now filter to just female patients"
- "Sort that by age descending"

---

### Extension 7: Real-Time Data Streaming

**Difficulty:** Hard | **Impact:** High

```python
# File: database/streaming_connector.py

import asyncio
from kafka import KafkaConsumer

class StreamingDataConnector:
    def __init__(self, stream_url: str):
        self.consumer = KafkaConsumer(stream_url)
    
    async def stream_to_db(self, table_name: str):
        """Stream data to SQLite table."""
        for message in self.consumer:
            data = json.loads(message.value)
            insert_to_db(table_name, data)
            
            # Trigger UI update
            st.experimental_rerun()

# File: ui/app.py
if st.checkbox("Enable Real-Time Updates"):
    streamer = StreamingDataConnector("kafka://localhost:9092")
    asyncio.run(streamer.stream_to_db("healthcare"))
```

---

### Extension 8: API Endpoint

**Difficulty:** Medium | **Impact:** High

```python
# File: api/server.py

from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class QueryRequest(BaseModel):
    question: str
    database: str
    session_id: str

@app.post("/query")
async def process_query(request: QueryRequest):
    # Initialize agent
    agent = SQLAgent(database=request.database)
    
    # Process query
    result = agent.query(request.question)
    
    return {
        "sql": result['sql_query'],
        "data": result['data'].to_dict(),
        "insights": result['insights'],
        "chart_url": upload_chart_to_s3(result['chart'])
    }

# Run with: uvicorn api.server:app --reload
```

**Enables:**
- External app integration
- Mobile app support
- Slack bot integration
- REST API for programmatic access

---

### Extension 9: User Authentication

**Difficulty:** Medium | **Impact:** High

```python
# File: auth/manager.py

import streamlit_authenticator as stauth

class AuthManager:
    def __init__(self):
        self.config = load_config('auth.yaml')
    
    def authenticate(self):
        authenticator = stauth.Authenticate(
            self.config['credentials'],
            self.config['cookie']['name'],
            self.config['cookie']['key'],
            self.config['cookie']['expiry_days']
        )
        
        name, auth_status, username = authenticator.login('Login', 'main')
        
        if auth_status:
            return username
        elif auth_status == False:
            st.error('Username/password is incorrect')
        elif auth_status == None:
            st.warning('Please enter your username and password')

# File: ui/app.py
auth = AuthManager()
username = auth.authenticate()

if username:
    # Show app
    run_app(username)
```

**Features:**
- Role-based access control
- Query history per user
- Saved visualizations
- Team collaboration

---

### Extension 10: Automated Insights Scheduling

**Difficulty:** Medium | **Impact:** Medium

```python
# File: scheduler/report_scheduler.py

from apscheduler.schedulers.background import BackgroundScheduler

class ReportScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
    
    def schedule_query(self, query: str, schedule: str, recipients: list):
        """
        Schedule recurring query execution.
        
        Args:
            query: SQL query or natural language
            schedule: Cron expression (e.g., "0 9 * * 1" = Monday 9am)
            recipients: Email list
        """
        self.scheduler.add_job(
            func=self.execute_and_email,
            trigger='cron',
            args=[query, recipients],
            **parse_cron(schedule)
        )
    
    def execute_and_email(self, query: str, recipients: list):
        # Execute query
        result = agent.query(query)
        
        # Generate PDF
        pdf = create_pdf_report(result)
        
        # Email
        send_email(recipients, subject="Scheduled Report", 
                  attachment=pdf)

# Usage
scheduler = ReportScheduler()
scheduler.schedule_query(
    query="Show weekly patient admissions",
    schedule="0 9 * * 1",  # Every Monday 9am
    recipients=["admin@hospital.com"]
)
scheduler.start()
```

---

## Summary

This SQL Data Analyst Agent is built with **production-ready architecture**, **modern AI techniques**, and **excellent user experience**. The modular design makes it easy to extend with new features, databases, or AI models.

### Key Strengths:
- ✅ **Clean 5-layer architecture** for maintainability
- ✅ **RAG implementation** for accurate SQL generation
- ✅ **Multi-database support** (5+ types)
- ✅ **Automatic error recovery** (up to 3 attempts)
- ✅ **Professional UI** with gradient design
- ✅ **FREE tier** (Groq 14,400 requests/day)
- ✅ **Extensible** design for future enhancements

### Future Enhancement Roadmap:
1. ✅ **Short-term:** Query caching, API endpoint
2. 🔄 **Mid-term:** Multi-language support, advanced visualizations
3. 🚀 **Long-term:** Real-time streaming, conversation memory, scheduled reports

The codebase is well-documented, follows Python best practices, and is ready for deployment.
