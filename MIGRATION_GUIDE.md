# 📋 Migration Guide: Multi-Database Update

## For Existing Users

If you've been using the SQL Data Analyst Agent with the fixed `sales_analytics.db` database, this guide will help you transition to the new multi-database architecture.

## What's Changed?

### ✨ New Features Added
- ✅ Upload any database file (.db, .sqlite, .csv)
- ✅ Connect to remote databases (MySQL, PostgreSQL, etc.)
- ✅ Automatic schema discovery
- ✅ Dynamic vector store creation
- ✅ Session-based multi-user support

### ✅ What Still Works
- ✅ All existing features (caching, validation, insights)
- ✅ Natural language queries
- ✅ Data visualizations
- ✅ PDF/HTML export
- ✅ Performance tracking
- ✅ Query history

### 🔄 What's Different
- **Database Setup Screen**: New first screen for connecting databases
- **Dynamic Agent**: Agent now adapts to any database schema
- **Session Management**: Each connection gets unique session ID

## Installation Steps

### 1. Install New Dependencies

```bash
pip install sqlalchemy pymysql psycopg2-binary sentence-transformers langchain-community
```

### 2. Update Your Workflow

#### Old Way (Fixed Database):
```bash
# Start app directly
streamlit run ui/app.py

# App automatically used sales_analytics.db
# Query immediately
```

#### New Way (Dynamic Database):
```bash
# Start app
streamlit run ui/app.py

# Choose database connection method:
# - Upload file OR
# - Enter connection string

# View discovered schema

# Click "Start Analyzing"

# Query as before
```

## Backward Compatibility

### Using the Original sales_analytics.db

**Option 1: Upload as File**
1. Navigate to your `data/` directory
2. Copy `sales_analytics.db`
3. Start the app
4. Click "Upload Database File"
5. Upload `sales_analytics.db`
6. All your data and queries work as before!

**Option 2: Use SQLite Connection String**
1. Start the app
2. Click "Connection String" tab
3. Select "SQLite"
4. Enter: `sqlite:///d:/Data_analyst_agent/data/sales_analytics.db`
5. Click "Connect"

### Your Existing Code

If you have custom scripts using the agent:

**Before**:
```python
from agent.sql_agent import SQLAgent

agent = SQLAgent()  # Uses default sales_analytics.db
result = agent.query("What's the total revenue?")
```

**After (Option 1 - Still works!)**:
```python
from agent.sql_agent import SQLAgent

agent = SQLAgent()  # Still works with default DB
result = agent.query("What's the total revenue?")
```

**After (Option 2 - With custom database)**:
```python
from agent.sql_agent import SQLAgent
from sqlalchemy import create_engine
from rag.dynamic_vector_store import DynamicVectorStore

# Connect to your database
engine = create_engine('sqlite:///my_database.db')

# Create vector store
vector_store = DynamicVectorStore()
vectorstore = vector_store.initialize_for_session('my_session', engine)

# Create agent with dynamic connection
agent = SQLAgent(engine=engine, vectorstore=vectorstore)
result = agent.query("What's the total revenue?")
```

## File Structure Changes

### New Files Added:
```
database/
  ├── connection_manager.py      # NEW: Multi-DB connection handling
  └── schema_discoverer.py       # NEW: Automatic schema analysis

rag/
  └── dynamic_vector_store.py    # NEW: Session-based vector stores

data/
  └── session_vector_stores/     # NEW: Per-session vector stores
      └── {session-id}/

uploads/
  └── {session-id}/              # NEW: Uploaded database files
```

### Modified Files:
- `ui/app.py` - Added database setup workflow
- `ui/components.py` - Added `render_database_setup()`
- `agent/sql_agent.py` - Added dynamic mode support
- `requirements.txt` - Added new dependencies

### Unchanged Files:
- All existing features remain intact
- `config/settings.py` - Still used for API keys
- `database/db_manager.py` - Still works for default mode
- `rag/vector_store.py` - Still works for default mode
- All visualization and export code unchanged

## Testing Your Migration

### 1. Test with Sample CSV
```bash
# Use the included sample_data.csv
streamlit run ui/app.py
# Upload sample_data.csv
# Ask: "What's the total revenue?"
```

### 2. Test with Original Database
```bash
# Upload your existing sales_analytics.db
streamlit run ui/app.py
# Upload data/sales_analytics.db
# Run your usual queries
```

### 3. Verify Features Work
- [ ] Query execution
- [ ] Data visualization
- [ ] PDF export
- [ ] Cache hits (run same query twice)
- [ ] Performance stats
- [ ] Example questions in sidebar

## Troubleshooting

### "Import errors" when starting
```bash
# Install missing dependencies
pip install sqlalchemy pymysql psycopg2-binary sentence-transformers langchain-community
```

### "No module named 'langchain_community'"
```bash
pip install langchain-community
```

### App shows old interface (no database setup)
- Clear Streamlit cache: Delete `.streamlit/` folder
- Restart the app
- Should show new database setup screen

### Queries failing after upload
- Check that schema discovery completed
- Verify "Start Analyzing" was clicked
- Check vector store was created (look for session_vector_stores/ folder)

### Performance slower than before
- First query on new database creates vector store (30-60 seconds)
- Subsequent queries use cache and are fast
- Vector store persists between sessions

## Rollback Plan

If you need to revert to the old version:

1. **Backup your current code**:
   ```bash
   git stash
   # or create a backup folder
   ```

2. **Revert to old version**:
   ```bash
   git checkout [commit-before-multi-db]
   ```

3. **Or keep using default mode**:
   - Just initialize agent without parameters: `SQLAgent()`
   - Works exactly as before

## Benefits of Migrating

1. **Flexibility**: Use any database, not just sales_analytics.db
2. **CSV Support**: Upload CSV files instantly
3. **Remote Databases**: Connect to MySQL, PostgreSQL servers
4. **Multi-User**: Support multiple users with different databases
5. **Schema Learning**: Agent learns any database structure
6. **Future-Proof**: Ready for any data source

## Support

For issues or questions:
1. Check `MULTI_DATABASE_GUIDE.md` for detailed documentation
2. Check `IMPLEMENTATION_SUMMARY.md` for technical details
3. Review error messages in terminal
4. Check Streamlit logs

## Summary

✅ **Backward compatible** - Old code still works
✅ **New features available** - Upload any database
✅ **Easy migration** - Just install dependencies
✅ **Same performance** - Caching and optimization maintained
✅ **Better UX** - Visual database setup screen

**Ready to use your own data! 🎉**
