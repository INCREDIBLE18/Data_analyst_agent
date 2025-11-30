# 🚀 Deployment & Production Guide

## Quick Start (Development)

### 1. Prerequisites
```bash
# Check Python version (must be 3.10+)
python --version

# Ensure pip is updated
python -m pip install --upgrade pip
```

### 2. Installation
```bash
# Clone/navigate to project
cd Data_analyst_agent

# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows PowerShell:
.\venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration
```bash
# Copy environment template
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Edit .env file and add your OpenAI API key
# Required: OPENAI_API_KEY=sk-your-key-here
```

### 4. Initialize
```bash
# Run setup (creates DB and vector store)
python setup.py
```

### 5. Run
```bash
# Start the application
streamlit run ui/app.py
```

**Application URL**: http://localhost:8501

---

## Production Deployment

### Option 1: Streamlit Cloud (Easiest)

#### Step 1: Prepare Repository
```bash
# Ensure all files are committed
git add .
git commit -m "Production ready"
git push origin main
```

#### Step 2: Deploy to Streamlit Cloud
1. Go to https://share.streamlit.io/
2. Sign in with GitHub
3. Click "New app"
4. Select your repository
5. Set main file: `ui/app.py`
6. Add secrets in the dashboard:
   - `OPENAI_API_KEY` = your-key-here

#### Step 3: Advanced Settings
```toml
# .streamlit/config.toml
[server]
maxUploadSize = 200
enableCORS = false

[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
```

### Option 2: Docker Deployment

#### Dockerfile
```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Initialize database
RUN python setup.py

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Run application
CMD ["streamlit", "run", "ui/app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

#### docker-compose.yml
```yaml
version: '3.8'

services:
  sql-analyst:
    build: .
    ports:
      - "8501:8501"
    environment:
      - OPENAI_API_KEY=${OPENAI_API_KEY}
    volumes:
      - ./data:/app/data
    restart: unless-stopped
```

#### Build and Run
```bash
# Build image
docker build -t sql-analyst-agent .

# Run container
docker run -d \
  -p 8501:8501 \
  -e OPENAI_API_KEY=your-key-here \
  --name sql-analyst \
  sql-analyst-agent

# Or use docker-compose
docker-compose up -d
```

### Option 3: Cloud Platform (AWS/GCP/Azure)

#### AWS EC2 Deployment

**1. Launch EC2 Instance**
```bash
# Amazon Linux 2 or Ubuntu 20.04+
# Instance type: t2.medium (minimum)
# Security group: Allow 8501 inbound
```

**2. Setup Environment**
```bash
# SSH into instance
ssh -i your-key.pem ec2-user@your-instance-ip

# Update system
sudo yum update -y  # Amazon Linux
# or
sudo apt update && sudo apt upgrade -y  # Ubuntu

# Install Python 3.10+
sudo yum install python3.10 -y  # Amazon Linux
# or
sudo apt install python3.10 python3.10-venv -y  # Ubuntu

# Clone repository
git clone your-repo-url
cd Data_analyst_agent
```

**3. Install and Run**
```bash
# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export OPENAI_API_KEY=your-key-here

# Run setup
python setup.py

# Run with nohup for persistence
nohup streamlit run ui/app.py --server.port 8501 &
```

**4. Setup Process Manager (PM2/Systemd)**
```bash
# Install PM2
npm install -g pm2

# Create ecosystem file
cat > ecosystem.config.js << EOF
module.exports = {
  apps: [{
    name: 'sql-analyst',
    script: 'streamlit',
    args: 'run ui/app.py --server.port 8501',
    interpreter: 'venv/bin/python',
    env: {
      OPENAI_API_KEY: 'your-key-here'
    }
  }]
}
EOF

# Start with PM2
pm2 start ecosystem.config.js
pm2 save
pm2 startup
```

#### Systemd Service (Alternative)
```ini
# /etc/systemd/system/sql-analyst.service
[Unit]
Description=SQL Data Analyst Agent
After=network.target

[Service]
Type=simple
User=ec2-user
WorkingDirectory=/home/ec2-user/Data_analyst_agent
Environment="PATH=/home/ec2-user/Data_analyst_agent/venv/bin"
Environment="OPENAI_API_KEY=your-key-here"
ExecStart=/home/ec2-user/Data_analyst_agent/venv/bin/streamlit run ui/app.py --server.port 8501
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start service
sudo systemctl enable sql-analyst
sudo systemctl start sql-analyst
sudo systemctl status sql-analyst
```

---

## Production Configuration

### Environment Variables

**Required:**
```bash
OPENAI_API_KEY=sk-proj-...        # Your OpenAI API key
```

**Optional:**
```bash
DATABASE_PATH=data/sales_analytics.db
CHROMA_PERSIST_DIR=data/chroma_db
LLM_MODEL=gpt-4-turbo-preview
LLM_TEMPERATURE=0.0
MAX_REPAIR_ATTEMPTS=3
```

### Security Checklist

- [ ] API keys stored in environment variables (not in code)
- [ ] .env file in .gitignore
- [ ] HTTPS enabled for production
- [ ] Rate limiting configured
- [ ] Input validation enabled
- [ ] Error messages sanitized
- [ ] Logging configured
- [ ] Backup strategy in place

### Performance Tuning

#### 1. Streamlit Configuration
```toml
# .streamlit/config.toml
[server]
maxUploadSize = 200
enableXsrfProtection = true
enableCORS = false
port = 8501

[browser]
gatherUsageStats = false
serverAddress = "0.0.0.0"

[client]
toolbarMode = "minimal"
showErrorDetails = false
```

#### 2. Database Optimization
```python
# Add indexes for frequently queried columns
# In database/db_setup.py:
cursor.execute("CREATE INDEX idx_orders_date ON orders(order_date)")
cursor.execute("CREATE INDEX idx_orders_customer ON orders(customer_id)")
cursor.execute("CREATE INDEX idx_items_order ON order_items(order_id)")
```

#### 3. Caching Strategy
```python
# Add caching in ui/app.py
@st.cache_resource
def load_agent():
    return SQLAgent()

@st.cache_data(ttl=3600)
def execute_query(query: str):
    # Cache results for 1 hour
    return agent.query(query)
```

---

## Monitoring & Maintenance

### Logging

**Add logging to agent/sql_agent.py:**
```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)
```

### Health Checks

**Add health endpoint:**
```python
# ui/app.py
def health_check():
    """Health check for monitoring."""
    try:
        # Check database
        db_manager = DatabaseManager()
        db_manager.get_table_names()
        
        # Check vector store
        vector_store = VectorStore()
        vector_store.search_schema("test", n_results=1)
        
        return True
    except:
        return False
```

### Monitoring Metrics

**Track these metrics:**
- Query execution time
- Error rate
- API usage (tokens)
- Active users
- Database size
- Response time

### Backup Strategy

```bash
# Daily database backup
0 2 * * * /usr/bin/rsync -av /app/data/sales_analytics.db /backup/db_$(date +\%Y\%m\%d).db

# Weekly full backup
0 3 * * 0 tar -czf /backup/full_$(date +\%Y\%m\%d).tar.gz /app/data
```

---

## Scaling Considerations

### Horizontal Scaling

**Load Balancer Setup:**
```nginx
# nginx.conf
upstream sql_analyst {
    server app1:8501;
    server app2:8501;
    server app3:8501;
}

server {
    listen 80;
    server_name your-domain.com;
    
    location / {
        proxy_pass http://sql_analyst;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### Database Scaling

**Move to PostgreSQL:**
```python
# config/settings.py
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:pass@host:5432/dbname"
)
```

### Caching Layer

**Add Redis:**
```python
import redis

redis_client = redis.Redis(
    host='localhost',
    port=6379,
    decode_responses=True
)

# Cache query results
def cached_query(query: str):
    cached = redis_client.get(f"query:{query}")
    if cached:
        return json.loads(cached)
    
    result = execute_query(query)
    redis_client.setex(
        f"query:{query}",
        3600,  # 1 hour TTL
        json.dumps(result)
    )
    return result
```

---

## Cost Optimization

### OpenAI API Usage

**Estimated costs per query:**
- SQL Generation: ~500-1000 tokens ($0.01-0.02)
- Insights Generation: ~300-500 tokens ($0.005-0.01)
- **Total per query: ~$0.015-0.03**

**Optimization strategies:**
1. Cache common queries
2. Use gpt-3.5-turbo for simpler queries
3. Batch similar queries
4. Implement rate limiting

### Infrastructure Costs

**AWS EC2 Example:**
- t2.medium: ~$30/month
- Storage (20GB): ~$2/month
- Data transfer: ~$5/month
- **Total: ~$37/month**

**Serverless Alternative:**
- AWS Lambda + API Gateway
- Pay per use
- Cost-effective for low traffic

---

## Troubleshooting Production Issues

### High API Costs
```python
# Add token counting
import tiktoken

def count_tokens(text: str) -> int:
    enc = tiktoken.encoding_for_model("gpt-4-turbo")
    return len(enc.encode(text))

# Monitor usage
logger.info(f"Tokens used: {count_tokens(prompt)}")
```

### Slow Performance
```python
# Add timing
import time

start = time.time()
result = agent.query(question)
duration = time.time() - start
logger.info(f"Query took {duration:.2f}s")
```

### Memory Issues
```python
# Clear caches periodically
st.cache_data.clear()
st.cache_resource.clear()
```

---

## Update & Maintenance

### Update Dependencies
```bash
# Check for updates
pip list --outdated

# Update specific package
pip install --upgrade streamlit

# Update all (carefully)
pip install -r requirements.txt --upgrade
```

### Database Migrations
```python
# Add migration script
# migrations/001_add_indexes.py
def migrate():
    conn = sqlite3.connect(settings.DATABASE_PATH)
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_orders_date ON orders(order_date)")
    conn.commit()
    conn.close()
```

### Rollback Strategy
```bash
# Keep previous version
cp -r /app /app.backup

# If issues, rollback
mv /app /app.failed
mv /app.backup /app
sudo systemctl restart sql-analyst
```

---

## Production Checklist

### Pre-Deployment
- [ ] All tests passing
- [ ] Documentation updated
- [ ] Environment variables set
- [ ] Database initialized
- [ ] Vector store created
- [ ] Backups configured
- [ ] Monitoring setup
- [ ] SSL certificate ready

### Deployment
- [ ] Code deployed
- [ ] Database migrated
- [ ] Services started
- [ ] Health check passing
- [ ] Logs monitored
- [ ] Performance tested

### Post-Deployment
- [ ] Monitor for errors
- [ ] Check API usage
- [ ] Verify functionality
- [ ] Collect user feedback
- [ ] Plan improvements

---

## Support & Resources

### Documentation
- README.md - Main guide
- ARCHITECTURE.md - Technical details
- TROUBLESHOOTING.md - Common issues
- VISUAL_GUIDE.md - Diagrams

### Monitoring Tools
- **Logs**: Application logs in `logs/`
- **Metrics**: Streamlit analytics
- **Health**: Custom health check endpoint
- **APM**: Consider New Relic or DataDog

### Useful Commands
```bash
# Check status
sudo systemctl status sql-analyst

# View logs
tail -f logs/app.log

# Restart service
sudo systemctl restart sql-analyst

# Check disk space
df -h

# Monitor resources
htop
```

---

**Production Deployment Complete!** 🎉

The application is now ready for production use with proper monitoring, security, and scalability.
