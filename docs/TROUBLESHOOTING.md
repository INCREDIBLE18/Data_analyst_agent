# Troubleshooting Guide

## Common Issues and Solutions

### 1. "OPENAI_API_KEY not found"

**Problem:** The application can't find your OpenAI API key.

**Solution:**
```bash
# 1. Make sure .env file exists
copy .env.example .env

# 2. Edit .env and add your API key
# Open .env in a text editor and add:
OPENAI_API_KEY=sk-your-actual-api-key-here

# 3. Restart the application
```

### 2. "Module not found" errors

**Problem:** Python packages are not installed.

**Solution:**
```bash
# Install all required packages
pip install -r requirements.txt

# If you're using a virtual environment, make sure it's activated:
# Windows:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### 3. "Database file not found"

**Problem:** The SQLite database hasn't been created yet.

**Solution:**
```bash
# Run the setup script
python setup.py

# Or create manually
python -m database.db_setup
```

### 4. Chroma initialization errors

**Problem:** Vector store can't be initialized.

**Solution:**
```bash
# Delete the Chroma directory and recreate
rmdir /s data\chroma_db  # Windows
rm -rf data/chroma_db    # Linux/Mac

# Run setup again
python setup.py
```

### 5. "Rate limit exceeded" from OpenAI

**Problem:** Too many API requests.

**Solution:**
- Wait a few minutes before trying again
- Check your OpenAI API usage at platform.openai.com
- Upgrade your OpenAI plan if needed

### 6. Streamlit won't start

**Problem:** Port already in use or Streamlit not installed.

**Solution:**
```bash
# Try a different port
streamlit run ui/app.py --server.port 8502

# Reinstall Streamlit
pip install --upgrade streamlit
```

### 7. SQL queries return no results

**Problem:** Query is correct but no data matches.

**Solution:**
- Check the example queries in the sidebar
- Try broader queries first (e.g., "List all customers")
- View the generated SQL to understand what was queried

### 8. Charts not displaying

**Problem:** Plotly charts don't render.

**Solution:**
```bash
# Update Plotly
pip install --upgrade plotly

# Clear Streamlit cache
streamlit cache clear
```

### 9. Slow query execution

**Problem:** Queries take too long.

**Solution:**
- The first query is slower (initializing agent)
- Subsequent queries should be faster
- Check your internet connection (for LLM calls)
- Simplify complex queries

### 10. Import errors with langchain

**Problem:** `ImportError: cannot import name 'ChatOpenAI' from 'langchain_openai'`

**Solution:**
```bash
# Install the correct version
pip install langchain==0.1.9 langchain-openai==0.0.5

# If issues persist, reinstall all dependencies
pip uninstall langchain langchain-openai -y
pip install -r requirements.txt
```

## Debugging Tips

### Enable Verbose Mode

Edit `agent/sql_agent.py` and change:
```python
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True,  # Change to True
    # ...
)
```

### Check Logs

The application prints helpful debug information to the console:
- 🤔 Processing query
- 📝 Generated SQL
- ⚠️ Query errors
- 🔧 Repair attempts
- ✅ Success messages

### Test Components Individually

```bash
# Test database setup
python -m database.db_setup

# Test vector store (in Python shell)
python
>>> from rag.vector_store import initialize_vector_store
>>> vector_store = initialize_vector_store()

# Test agent (in Python shell)
python
>>> from agent.sql_agent import SQLAgent
>>> agent = SQLAgent()
>>> result = agent.query("List all customers")
>>> print(result)
```

### Check Python Version

```bash
python --version
# Should be 3.10 or higher
```

### Verify Environment Variables

```bash
# Windows PowerShell
Get-Content .env

# Linux/Mac
cat .env
```

## Performance Issues

### Slow Startup

**Normal:** First startup takes 30-60 seconds to:
- Initialize vector store
- Load embeddings
- Create agent

**Abnormal:** If it takes longer:
- Check internet connection
- Verify OpenAI API is accessible
- Try clearing the Chroma cache

### Slow Queries

**Expected times:**
- First query: 5-10 seconds
- Subsequent queries: 2-5 seconds
- Complex queries: 5-15 seconds

**If slower:**
- Check internet latency
- Verify OpenAI API status
- Simplify the query

## Getting Help

### Check Documentation
1. README.md - Complete guide
2. ARCHITECTURE.md - Technical details
3. QUICKSTART.md - Quick start
4. PROJECT_SUMMARY.md - Overview

### Debug Checklist
- [ ] Python 3.10+ installed
- [ ] All packages installed (`pip list`)
- [ ] .env file exists with API key
- [ ] Database created (`data/sales_analytics.db` exists)
- [ ] Vector store initialized (`data/chroma_db/` exists)
- [ ] Internet connection working
- [ ] OpenAI API key valid

### Error Messages

If you see an error, check:
1. **Configuration errors**: Check .env file
2. **Import errors**: Reinstall packages
3. **API errors**: Verify API key and quota
4. **Database errors**: Run setup.py again
5. **UI errors**: Clear browser cache and restart

## Advanced Troubleshooting

### Reset Everything

```bash
# 1. Stop the application (Ctrl+C)

# 2. Delete generated data
rmdir /s data  # Windows
rm -rf data    # Linux/Mac

# 3. Reinstall packages
pip install -r requirements.txt --force-reinstall

# 4. Run setup
python setup.py

# 5. Start application
streamlit run ui/app.py
```

### Check Dependencies

```bash
# List installed packages
pip list

# Compare with requirements
pip check

# Upgrade all packages
pip install -r requirements.txt --upgrade
```

### SQLite Issues

```bash
# Check if SQLite is available
python -c "import sqlite3; print(sqlite3.sqlite_version)"

# Should print version 3.x.x
```

### Network Issues

```bash
# Test OpenAI API connection
python -c "from openai import OpenAI; client = OpenAI(); print('OK')"
```

## Still Having Issues?

If you've tried everything and still have problems:

1. **Check the error message carefully** - It usually indicates the problem
2. **Search the error online** - Others may have faced the same issue
3. **Verify your environment** - Python version, OS, etc.
4. **Start fresh** - Delete everything and reinstall

## Common Error Codes

- **401 Unauthorized**: Invalid OpenAI API key
- **429 Rate Limit**: Too many requests, wait and retry
- **500 Internal Error**: OpenAI service issue, try again later
- **ModuleNotFoundError**: Package not installed, run `pip install`
- **FileNotFoundError**: Run `python setup.py`

---

Most issues are resolved by:
1. Ensuring .env has a valid API key
2. Running `python setup.py`
3. Restarting the application
