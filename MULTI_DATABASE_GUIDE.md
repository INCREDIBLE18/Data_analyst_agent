# Multi-Database SQL Analyst Agent

## 🚀 New Feature: Dynamic Database Support

The SQL Analyst Agent now supports **any database**! Upload your own database files or connect to remote databases via connection strings.

## 📊 Supported Databases

### File Upload
- **SQLite** (.db, .sqlite, .sqlite3)
- **CSV Files** (.csv) - Automatically converted to SQLite

### Connection Strings
- **MySQL** - `mysql+pymysql://user:password@host:port/database`
- **PostgreSQL** - `postgresql://user:password@host:port/database`
- **SQL Server** - `mssql+pyodbc://user:password@host/database?driver=ODBC+Driver+17+for+SQL+Server`
- **Oracle** - `oracle+cx_oracle://user:password@host:port/database`
- **SQLite** - `sqlite:///path/to/database.db`

## 🎯 Features

### Automatic Schema Discovery
When you connect to a database, the system automatically:
- Discovers all tables and columns
- Analyzes data types and relationships
- Generates sample data for context
- Creates column statistics (min, max, avg, unique counts)
- Builds foreign key relationship maps

### Dynamic Vector Store
For each database session:
- Creates isolated vector store for semantic search
- Indexes schema metadata for intelligent query understanding
- Supports natural language queries about your specific database
- Maintains context isolation between different databases

### Session Management
- Each database connection gets a unique session ID
- Isolated vector stores prevent cross-contamination
- Easy cleanup and disconnection
- Support for concurrent users with different databases

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│         Database Setup Screen               │
│  ┌─────────────┐       ┌─────────────┐     │
│  │ File Upload │       │ Connection  │     │
│  │   (.db)     │   OR  │   String    │     │
│  └─────────────┘       └─────────────┘     │
└──────────────┬──────────────────────────────┘
               │
               v
┌──────────────────────────────────────────────┐
│      DatabaseConnectionManager               │
│  • Detect database type                      │
│  • Handle file uploads                       │
│  • Parse connection strings                  │
│  • Create SQLAlchemy engine                  │
└──────────────┬───────────────────────────────┘
               │
               v
┌──────────────────────────────────────────────┐
│         SchemaDiscoverer                     │
│  • Discover tables and columns               │
│  • Analyze relationships                     │
│  • Generate statistics                       │
│  • Create sample data                        │
└──────────────┬───────────────────────────────┘
               │
               v
┌──────────────────────────────────────────────┐
│       DynamicVectorStore                     │
│  • Create session-based vector store         │
│  • Index schema documents                    │
│  • Enable semantic search                    │
│  • Provide context to LLM                    │
└──────────────┬───────────────────────────────┘
               │
               v
┌──────────────────────────────────────────────┐
│           SQLAgent                           │
│  • Generate SQL from natural language        │
│  • Execute queries on dynamic engine         │
│  • Return results and insights               │
└──────────────────────────────────────────────┘
```

## 📝 Usage Examples

### Example 1: Upload CSV File
1. Click "Upload Database File" tab
2. Upload your `sales_data.csv`
3. System automatically converts to SQLite
4. View discovered schema
5. Click "Start Analyzing"
6. Ask: "What were the total sales last month?"

### Example 2: Connect to MySQL
1. Click "Connection String" tab
2. Select "MySQL" from dropdown
3. Enter: `mysql+pymysql://user:pass@localhost:3306/mydb`
4. Click "Connect"
5. View discovered tables
6. Click "Start Analyzing"
7. Ask: "Show me top 10 customers by revenue"

### Example 3: Upload SQLite Database
1. Click "Upload Database File" tab
2. Upload your `my_database.db`
3. System analyzes schema
4. View tables, columns, and relationships
5. Click "Start Analyzing"
6. Ask questions naturally about your data

## 🔧 New Components

### database/connection_manager.py
- Manages database connections
- Handles file uploads and connection strings
- Auto-detects database types
- Provides session-based isolation

### database/schema_discoverer.py
- Discovers complete database schema
- Analyzes column statistics
- Generates natural language descriptions
- Creates documents for vectorization

### rag/dynamic_vector_store.py
- Creates session-based vector stores
- Manages schema embeddings
- Provides semantic search
- Handles cleanup and rebuilding

## 🎨 UI Updates

### ui/components.py
- New `render_database_setup()` function
- File upload interface
- Connection string input
- Schema visualization
- Real-time connection status

### ui/app.py
- Database connection workflow
- Session management
- Dynamic agent initialization
- Connection info display

## 🧪 Testing

To test the multi-database functionality:

1. **SQLite Test**:
   ```python
   # Create test database
   import sqlite3
   conn = sqlite3.connect('test.db')
   conn.execute('CREATE TABLE users (id INT, name TEXT, age INT)')
   conn.execute("INSERT INTO users VALUES (1, 'Alice', 30), (2, 'Bob', 25)")
   conn.commit()
   ```
   Upload `test.db` and ask: "How many users are there?"

2. **CSV Test**:
   Create `sales.csv`:
   ```csv
   product,quantity,price
   Widget,10,25.99
   Gadget,5,49.99
   ```
   Upload and ask: "What's the total revenue?"

3. **MySQL Test** (if you have MySQL running):
   ```
   mysql+pymysql://root:password@localhost:3306/testdb
   ```

## 🔒 Security

- SQL validation prevents dangerous operations (DROP, DELETE, TRUNCATE)
- Connection strings are masked in UI
- Session isolation prevents data leakage
- Uploaded files are stored securely
- Automatic cleanup on disconnect

## 🚀 Performance

- **Query Caching**: 30-minute TTL reduces redundant queries
- **Vector Store**: Fast semantic search for schema understanding
- **Session-Based**: Isolated stores for efficient memory usage
- **Lazy Loading**: Vectorstores loaded only when needed

## 📦 Dependencies

New dependencies required:
```bash
pip install pymysql          # MySQL support
pip install psycopg2-binary  # PostgreSQL support
pip install pyodbc           # SQL Server support
pip install cx_Oracle        # Oracle support
```

## 🎯 Future Enhancements

- [ ] Database connection pooling
- [ ] Support for MongoDB (NoSQL)
- [ ] Query history per database
- [ ] Export schema to JSON/YAML
- [ ] Multi-database join queries
- [ ] Automatic index recommendations
- [ ] Query performance profiling
- [ ] Database backup/export

## 🆘 Troubleshooting

**Connection Failed?**
- Check connection string format
- Verify database credentials
- Ensure database is accessible
- Check firewall settings

**Schema Discovery Issues?**
- Ensure database has tables
- Check user permissions
- Verify database is not empty

**Query Execution Errors?**
- Check SQL syntax for your database type
- Verify column names in query
- Ensure data types are compatible

## 📄 License

Same as main project.
