# SQL Data Analyst Agent - Architecture Documentation

## System Overview

The SQL Data Analyst Agent is a production-grade AI system that converts natural language queries into SQL, executes them on a database, visualizes results, and provides intelligent insights.

## Architecture Layers

### 1. Configuration Layer (`config/`)
**Purpose:** Centralized configuration management

**Components:**
- `settings.py`: Environment variables, API keys, paths, and application settings
- Validates required configuration on startup
- Ensures all required directories exist

**Key Responsibilities:**
- Load environment variables from `.env`
- Provide type-safe access to configuration
- Validate API keys and paths
- Manage directory structure

### 2. Database Layer (`database/`)
**Purpose:** Database schema management and query execution

**Components:**
- `db_setup.py`: SQLite schema creation and sample data population
- `db_manager.py`: Database connection management and query execution

**Schema:**
```
customers (id, name, email, country, segment, created_at)
products (id, name, category, price, created_at)
orders (id, customer_id, order_date, status, total_amount)
order_items (id, order_id, product_id, quantity, unit_price)
```

**Key Responsibilities:**
- Create and initialize SQLite database
- Execute SQL queries safely
- Validate query syntax
- Provide schema introspection
- Generate database statistics

### 3. RAG Layer (`rag/`)
**Purpose:** Semantic search over database schema and documentation

**Components:**
- `schema_loader.py`: Extract and format database schema information
- `vector_store.py`: Manage Chroma vector database for schema embeddings

**RAG Pipeline:**
1. Extract database schema, sample data, and query patterns
2. Create embeddings using OpenAI's text-embedding-3-small
3. Store in Chroma vector database
4. Retrieve relevant schema context for queries

**Key Responsibilities:**
- Index database schema as vector embeddings
- Perform semantic search over schema documentation
- Provide relevant context to LLM for SQL generation
- Cache embeddings for performance

### 4. Agent Layer (`agent/`)
**Purpose:** LangChain-based agentic workflow for SQL generation and execution

**Components:**
- `sql_agent.py`: Main agent orchestrator using LangChain
- `tools.py`: Tool definitions for the agent
- `error_handler.py`: SQL error detection and repair loop

**Agent Tools:**
1. `search_schema`: Semantic search over database schema
2. `execute_sql`: Execute SQL queries
3. `get_table_info`: Get detailed table information
4. `list_tables`: List all available tables

**Error Repair Loop:**
```
1. Execute SQL query
2. If error: Extract error message
3. Use LLM to repair query with schema context
4. Retry execution (max 3 attempts)
5. Return results or final error
```

**Key Responsibilities:**
- Convert natural language to SQL using GPT-4
- Execute queries with error handling
- Automatically repair SQL errors using LLM
- Generate natural language insights from results

### 5. UI Layer (`ui/`)
**Purpose:** Clean, responsive Streamlit interface

**Components:**
- `app.py`: Main Streamlit application
- `components.py`: Reusable UI components
- `visualizer.py`: Automatic chart generation

**Features:**
- Natural language query input
- Example query suggestions
- SQL query display
- Interactive data tables
- Automatic visualizations
- AI-generated insights
- Key metrics dashboard

**Key Responsibilities:**
- Render user interface
- Handle user interactions
- Display query results
- Generate appropriate visualizations
- Show insights and metrics

## Data Flow

```
User Question (Natural Language)
    ↓
[Streamlit UI] Captures input
    ↓
[SQL Agent] Processes query
    ↓
[RAG Layer] Retrieves relevant schema context
    ↓
[LLM - GPT-4] Generates SQL query
    ↓
[Database Manager] Executes SQL
    ↓
[Error Handler] Repairs if needed (loop)
    ↓
[Visualizer] Auto-generates charts
    ↓
[LLM - GPT-4] Generates insights
    ↓
[Streamlit UI] Displays results
    ↓
User sees: SQL, Data Table, Chart, Insights
```

## Technology Stack

### Backend
- **Python 3.10+**: Core language
- **SQLite**: Embedded database
- **Pandas**: Data manipulation

### AI/ML
- **LangChain**: Agent framework and orchestration
- **OpenAI GPT-4 Turbo**: Natural language understanding and SQL generation
- **OpenAI text-embedding-3-small**: Schema embeddings
- **Chroma**: Vector database for semantic search

### Frontend
- **Streamlit**: Web application framework
- **Plotly**: Interactive visualizations

### Infrastructure
- **python-dotenv**: Environment management
- **Pydantic**: Data validation

## Design Patterns

### 1. Separation of Concerns
Each module has a single, well-defined responsibility:
- Config: Settings and environment
- Database: Data storage and queries
- RAG: Semantic search
- Agent: AI orchestration
- UI: User interface

### 2. Dependency Injection
Components receive their dependencies rather than creating them:
```python
class SQLAgent:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.vector_store = VectorStore()
        self.error_handler = SQLErrorHandler(self.db_manager)
```

### 3. Error Handling with Recovery
Automatic error repair loop with configurable retry attempts:
```python
def execute_with_retry(query, max_attempts=3):
    for attempt in range(max_attempts):
        result, error = execute(query)
        if not error:
            return result
        query = repair_query(query, error)
    return final_error
```

### 4. RAG Pattern
Retrieval-Augmented Generation for context-aware SQL generation:
```python
1. User asks question
2. Retrieve relevant schema from vector DB
3. Provide schema context to LLM
4. Generate SQL with full context
```

### 5. Tool-Based Agent
LangChain agent with specialized tools:
```python
tools = [
    search_schema_tool,
    execute_sql_tool,
    get_table_info_tool,
    list_tables_tool
]
agent = create_agent(llm, tools)
```

## Scalability Considerations

### Current Implementation
- Single SQLite database
- In-memory Chroma with persistence
- Synchronous query execution
- Session-based state management

### Production Enhancements
1. **Database**: PostgreSQL/MySQL for concurrent access
2. **Vector Store**: Cloud-hosted Chroma or Pinecone
3. **Caching**: Redis for query result caching
4. **Authentication**: User authentication and authorization
5. **Logging**: Structured logging with ELK stack
6. **Monitoring**: Query performance metrics
7. **Rate Limiting**: API request throttling
8. **Query Queue**: Async query execution
9. **Multi-tenancy**: Separate schemas per user/org

## Extension Points

### Adding New Databases
1. Create new connection class in `database/`
2. Implement query execution interface
3. Update schema loader for new database type
4. No changes needed in agent or UI

### Adding New LLM Providers
1. Update `config/settings.py` with new credentials
2. Replace OpenAI client in `agent/sql_agent.py`
3. Update embedding function in `rag/vector_store.py`

### Adding New Visualizations
1. Add detection logic in `visualizer.py`
2. Implement chart creation method
3. Charts automatically appear in UI

### Adding New Agent Tools
1. Create tool function in `agent/tools.py`
2. Add to `get_langchain_tools()` list
3. Agent automatically uses new tool

## Security Considerations

### Current Implementation
- Environment-based API key management
- SQL injection prevention via parameterized queries
- Read-only query execution (no DDL/DML beyond setup)

### Production Requirements
1. **Authentication**: OAuth/SAML integration
2. **Authorization**: Role-based access control
3. **Encryption**: Data at rest and in transit
4. **Audit Logging**: Query history and access logs
5. **Input Validation**: Strict query validation
6. **Rate Limiting**: Prevent abuse
7. **API Key Rotation**: Automated credential rotation

## Performance Optimization

### Query Execution
- Database indexes on frequently queried columns
- Query result caching for repeated queries
- Connection pooling for concurrent requests

### Vector Search
- Embedding caching to avoid recomputation
- Batch embedding generation during setup
- Incremental index updates

### LLM Calls
- Response caching for similar queries
- Streaming responses for large results
- Token usage optimization

## Testing Strategy

### Unit Tests
- Database operations
- Schema loading
- Query validation
- Error handling

### Integration Tests
- End-to-end query flow
- Agent tool execution
- Vector search accuracy
- UI component rendering

### Performance Tests
- Query execution time
- LLM response latency
- Concurrent user load
- Vector search speed

## Monitoring and Observability

### Metrics to Track
- Query execution time
- Error rate and types
- LLM token usage
- User query patterns
- Chart generation time

### Logging
- Structured JSON logs
- Query audit trail
- Error stack traces
- Performance metrics

### Alerts
- High error rates
- Slow query performance
- API quota limits
- System resource usage

## Conclusion

This architecture provides a solid foundation for a production SQL Data Analyst Agent with:
- Clean separation of concerns
- Extensible design
- Robust error handling
- Smart visualizations
- Context-aware SQL generation
- Production-ready patterns

The modular design makes it easy to extend to other databases, LLM providers, or add new features without major refactoring.
