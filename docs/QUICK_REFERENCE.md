# 🎯 Quick Reference - SQL Data Analyst Agent

## 📍 Access Points
- **Local**: http://localhost:8501
- **Network**: http://10.205.112.153:8501

## ⚡ Start/Stop Commands

**Start the app:**
```powershell
streamlit run ui/app.py
```

**Stop the app:**
Press `Ctrl+C` in the terminal

**Restart after code changes:**
```powershell
# Stop (Ctrl+C), then:
streamlit run ui/app.py
```

## 🗂️ Database Schema

| Table | Columns | Purpose |
|-------|---------|---------|
| `customers` | id, name, email, country, segment | Customer information |
| `products` | id, name, category, price | Product catalog |
| `orders` | id, customer_id, order_date, status, total_amount | Order transactions |
| `order_items` | id, order_id, product_id, quantity, unit_price | Order line items |

## 💬 Sample Queries by Type

### 📋 Simple Select
```
Show me all customers
List all products
Show me recent orders
Display products in Electronics category
```

### 📊 Aggregations
```
What is the total revenue?
How many orders do we have?
What is the average order value?
Show me the count of customers by country
```

### 🏆 Top/Bottom N
```
What are the top 5 products by revenue?
Show me the top 10 customers by total spending
What are the bottom 5 products by sales?
```

### 📅 Time-Based
```
Show orders from January 2024
What are monthly sales for 2023?
How many orders per month?
Show sales trends over time
```

### 🔗 Joins
```
Show orders with customer names
List products with their total revenue
Show customers and their order count
Display orders with product details
```

### 🔍 Complex Filters
```
Which customers have spent more than $1000?
Show products that have never been ordered
What is the average price by product category?
Show customers who placed orders in Q1 2024
```

### 📈 Analytics
```
What is total revenue by customer segment?
Show monthly revenue trends
Which product category generates most revenue?
What is the average number of items per order?
```

## 🎨 Chart Types

The app automatically chooses the best chart:

- **Time series data** → Line chart
- **Categories** → Bar chart  
- **Distributions** → Pie chart
- **Single metrics** → KPI card
- **Comparisons** → Bar/Column chart

## ⚙️ Configuration Files

| File | Purpose | Location |
|------|---------|----------|
| `.env` | API keys and settings | Project root |
| `requirements.txt` | Python packages | Project root |
| `data/sales_analytics.db` | SQLite database | data/ folder |
| `data/chroma_db/` | Vector embeddings | data/ folder |

## 🔧 Key Settings (.env)

```env
# LLM Provider
LLM_PROVIDER=groq
GROQ_API_KEY=your-groq-api-key-here
LLM_MODEL=llama-3.3-70b-versatile
LLM_TEMPERATURE=0.0

# Database
DATABASE_PATH=./data/sales_analytics.db

# Vector Store
CHROMA_PERSIST_DIR=./data/chroma_db
CHROMA_COLLECTION_NAME=sql_schema
```

## 🐛 Common Issues & Fixes

| Issue | Solution |
|-------|----------|
| Import errors | Restart VS Code or ignore (code works) |
| App won't start | Check Groq API key in `.env` |
| Query fails | Rephrase question, check error message |
| No charts | Ensure query returns data |
| Slow response | Normal for first query (model loading) |

## 📊 Query Tips

✅ **DO:**
- Be specific ("top 5 products" not "best products")
- Use time ranges ("January 2024" not "recent")
- Specify columns ("show name and revenue")
- Ask one thing at a time

❌ **DON'T:**
- Use vague terms ("some", "a few", "recent")
- Mix multiple unrelated questions
- Ask for data that doesn't exist
- Use complex SQL-specific terminology

## 🎯 Keyboard Shortcuts (in browser)

- `Ctrl+Enter` - Submit query
- `Ctrl+R` - Reload page
- `Ctrl+Shift+R` - Hard reload (clear cache)
- `F5` - Refresh page

## 📝 Project Structure

```
Data_analyst_agent/
├── agent/          # LangChain agent and tools
├── config/         # Settings and configuration
├── database/       # Database setup and management
├── rag/            # Vector store and schema loader
├── ui/             # Streamlit interface
├── data/           # Databases and embeddings
└── docs/           # Documentation
```

## 🔄 Workflow

```
User Question
    ↓
Schema Search (RAG)
    ↓
SQL Generation (Groq LLM)
    ↓
Execute Query (SQLite)
    ↓
Error? → Repair & Retry (3x max)
    ↓
Generate Chart (Plotly)
    ↓
Generate Insights (Groq LLM)
    ↓
Display Results
```

## 💰 Cost & Limits

**Groq Free Tier:**
- 14,400 requests/day
- 30 requests/minute
- More than enough for development!

**Embeddings:**
- Completely free (local ONNX model)
- No API calls
- No rate limits

## 📚 Documentation

| File | Content |
|------|---------|
| `README.md` | Project overview |
| `GROQ_SETUP.md` | Groq API setup |
| `QUICKSTART.md` | 5-minute setup |
| `SETUP_COMPLETE.md` | **This guide** |
| `PROJECT_STATUS.md` | Detailed status |
| `docs/USER_GUIDE.md` | Full user manual |
| `docs/ARCHITECTURE.md` | Technical design |
| `docs/API.md` | Code reference |

## 🆘 Get Help

1. Check error message in UI
2. Look at generated SQL
3. Read `docs/FAQ.md`
4. Check terminal for errors
5. Review `docs/USER_GUIDE.md`

## 🎉 Quick Test

Try this to verify everything works:

1. Open http://localhost:8501
2. Type: "Show me all customers"
3. Click "Run Query"
4. Should see: SQL query, results table, and insights

**If you see results → Everything works! 🎊**

---

## 📌 Important Files

**Must have correct values:**
- `.env` - Groq API key

**Generated automatically:**
- `data/sales_analytics.db` - Database
- `data/chroma_db/` - Embeddings

**Can modify:**
- `database/db_setup.py` - Add your own data
- `ui/components.py` - Customize UI
- `agent/tools.py` - Add new tools

---

**Your SQL Data Analyst Agent is ready to use!** 🚀

Access it at: **http://localhost:8501**
