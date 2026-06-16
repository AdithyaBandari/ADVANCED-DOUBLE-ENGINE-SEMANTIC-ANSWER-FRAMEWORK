# 🚀 Deployment Guide

This guide covers deploying the Semantic Answer Framework to production environments.

## Table of Contents

1. [Local Deployment](#local-deployment)
2. [Streamlit Cloud](#streamlit-cloud)
3. [Docker Deployment](#docker-deployment)
4. [Self-Hosted Solutions](#self-hosted-solutions)
5. [Security Best Practices](#security-best-practices)

---

## Local Deployment

### Basic Setup

```bash
# Clone/download project
git clone <repository-url>
cd semantic-answer-framework

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set API key
export GROQ_API_KEY="your-api-key"  # Windows: set GROQ_API_KEY=your-api-key

# Run app
streamlit run app.py
```

### Access the App

- Local: `http://localhost:8501`
- Network: `http://YOUR_IP:8501`

---

## Streamlit Cloud

Streamlit Cloud is the easiest way to deploy for free.

### Prerequisites

- GitHub account
- Code pushed to GitHub repository
- Streamlit account

### Step 1: Prepare Your Repository

```bash
# Ensure these files are in your repo:
- app.py (or app_production.py)
- requirements.txt
- .streamlit/config.toml (optional)
```

### Step 2: Create .streamlit/config.toml

```toml
[client]
showErrorDetails = true

[server]
maxUploadSize = 200
timeout = 3600

[logger]
level = "info"
```

### Step 3: Create .streamlit/secrets.toml (Local Testing)

```toml
GROQ_API_KEY = "your-api-key-here"
```

**Do NOT commit this to GitHub!**

### Step 4: Deploy to Streamlit Cloud

1. Go to [share.streamlit.io](https://share.streamlit.io)
2. Click "New app"
3. Select your GitHub repo
4. Select branch and file (`app_production.py`)
5. Click "Deploy"

### Step 5: Add Secrets in Dashboard

1. Go to your app's settings
2. Click "Secrets"
3. Add:
```
GROQ_API_KEY = "your-production-api-key"
```

### Step 6: Access Your App

Your app will be live at: `https://[username]-[appname].streamlit.app`

### Managing Streamlit Cloud App

- **Rerun**: Push changes to GitHub (auto-deploys)
- **Monitor**: Check logs in dashboard
- **Share**: Click "Share" button for sharing link
- **Settings**: Manage secrets and compute resources

---

## Docker Deployment

Deploy using Docker for consistent environments.

### Create Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy files
COPY requirements.txt .
COPY app.py .
COPY .streamlit/ .streamlit/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8501

# Health check
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health

# Run app
CMD ["streamlit", "run", "app_production.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Create docker-compose.yml

```yaml
version: '3.8'

services:
  semantic-app:
    build: .
    ports:
      - "8501:8501"
    environment:
      - GROQ_API_KEY=${GROQ_API_KEY}
      - LOG_LEVEL=INFO
    volumes:
      - ./uploads:/app/uploads
      - ./cache:/app/.cache
    restart: unless-stopped
```

### Build and Run

```bash
# Set API key
export GROQ_API_KEY="your-api-key"

# Build image
docker build -t semantic-app .

# Run container
docker run -p 8501:8501 \
  -e GROQ_API_KEY=$GROQ_API_KEY \
  semantic-app

# Or use docker-compose
docker-compose up
```

### Access

Visit `http://localhost:8501`

---

## Self-Hosted Solutions

### Option 1: AWS EC2

```bash
# Launch Ubuntu instance
# SSH into instance

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install -y python3-pip python3-venv git

# Clone repository
git clone <your-repo>
cd semantic-answer-framework

# Setup virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
pip install -r requirements.txt

# Set environment variables
export GROQ_API_KEY="your-api-key"

# Run with nohup (background process)
nohup streamlit run app_production.py \
  --server.port=80 \
  --server.address=0.0.0.0 > output.log 2>&1 &

# Or use systemd service (better for production)
# Create /etc/systemd/system/semantic-app.service
```

### Option 2: Heroku (Legacy - Use Alternatives)

Heroku has discontinued free tier. Use:
- **Railway.app** (similar to Heroku)
- **Render.com** (free tier available)
- **PythonAnywhere** (Python-specific hosting)

### Option 3: DigitalOcean App Platform

```yaml
name: semantic-framework
services:
- name: web
  github:
    branch: main
    repo: username/semantic-framework
  http_port: 8501
  envs:
  - key: GROQ_API_KEY
    scope: RUN_AND_BUILD_TIME
    value: ${GROQ_API_KEY}
```

---

## Security Best Practices

### 1. API Key Management

**❌ NEVER:**
```python
os.environ['GROQ_API_KEY'] = 'gsk_...'  # Hardcoded
```

**✅ ALWAYS:**
```python
api_key = os.getenv('GROQ_API_KEY')
if not api_key:
    raise ValueError("GROQ_API_KEY not set")
```

### 2. Environment Variables

**Local:**
```bash
# Linux/Mac
export GROQ_API_KEY="your-key"
streamlit run app.py

# Windows PowerShell
$env:GROQ_API_KEY = "your-key"
streamlit run app.py
```

**Deployment:**
- Streamlit Cloud: Use dashboard secrets
- Docker: Use `docker secrets` or `.env` files
- AWS: Use IAM/Secrets Manager
- Never commit `.env` files!

### 3. .gitignore

```
# Environment variables
.env
.env.local
secrets.toml

# Cache directories
.cache/
__pycache__/
*.pyc

# Sensitive files
*.key
*.pem
config.ini

# OS files
.DS_Store
Thumbs.db
```

### 4. API Rate Limiting

```python
from functools import wraps
import time

def rate_limit(calls_per_minute=20):
    min_interval = 60.0 / calls_per_minute
    last_called = [0.0]
    
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            elapsed = time.time() - last_called[0]
            if elapsed < min_interval:
                time.sleep(min_interval - elapsed)
            result = func(*args, **kwargs)
            last_called[0] = time.time()
            return result
        return wrapper
    return decorator
```

### 5. Input Validation

```python
def validate_question(question: str) -> bool:
    """Validate user input"""
    # Check length
    if len(question) < 3:
        return False
    
    # Check for malicious content
    dangerous_keywords = ['--', ';', 'DROP', 'DELETE']
    if any(kw.lower() in question.lower() for kw in dangerous_keywords):
        return False
    
    return True
```

### 6. HTTPS/SSL

For production, always use HTTPS:

```python
# Streamlit Cloud: Automatic
# Docker/Self-hosted: Use Nginx reverse proxy
```

**Nginx configuration:**
```nginx
server {
    listen 443 ssl http2;
    server_name your-domain.com;
    
    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;
    
    location / {
        proxy_pass http://localhost:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### 7. Monitoring & Logging

```python
import logging
import sys

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('app.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)

# Log important events
logger.info("App started")
logger.warning("High API usage")
logger.error("API key not found")
```

### 8. Access Control

For multi-user deployments:

```python
import hashlib

def check_password(password):
    """Validate password"""
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    correct_hash = "your-stored-hash"
    return password_hash == correct_hash

if "authentication_status" not in st.session_state:
    password = st.text_input("Enter password", type="password")
    if password and check_password(password):
        st.session_state.authentication_status = True
    elif password:
        st.error("Invalid password")
        st.stop()
    else:
        st.stop()
```

---

## Performance Optimization

### Caching

```python
@st.cache_resource
def load_embedding_model():
    return HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )

@st.cache_data
def process_documents(files):
    # Process only once
    pass
```

### Reduce Memory Usage

```python
# Limit concurrent users
MAX_SESSIONS = 10

# Use smaller models
model_name = "all-MiniLM-L6-v2"  # Smaller, faster

# Reduce chunk size
chunk_size = 800  # Smaller chunks

# Limit retrieved documents
k = 3  # Fewer documents
```

---

## Monitoring in Production

### Key Metrics to Track

1. **API Usage**
   - Tokens consumed
   - Cost per query
   - Request success rate

2. **Performance**
   - Response time
   - Document processing time
   - Cache hit rate

3. **Errors**
   - Failed queries
   - API timeouts
   - Missing data

### Tools

- **Streamlit Cloud**: Built-in dashboard
- **Docker**: Prometheus + Grafana
- **AWS**: CloudWatch
- **DigitalOcean**: Monitoring tools

---

## Troubleshooting Deployment

### App won't start

```bash
# Check logs
streamlit logs

# Verify dependencies
pip list | grep langchain

# Test imports
python -c "import langchain; print(langchain.__version__)"
```

### Slow performance

- Check available memory
- Reduce concurrent users
- Use smaller models
- Increase server resources

### API errors

- Verify API key is correct
- Check rate limits
- Monitor API usage
- Use exponential backoff

---

## Comparison of Deployment Options

| Option | Cost | Ease | Customization | Scalability |
|--------|------|------|---------------|-------------|
| Local | Free | Easy | High | Limited |
| Streamlit Cloud | Free | Very Easy | Medium | Auto-scaling |
| Docker | Low | Medium | Very High | Manual |
| AWS | Medium | Hard | Very High | Excellent |
| DigitalOcean | Low | Medium | High | Good |
| Heroku Alternative | Low | Easy | Medium | Good |

---

## Support & Resources

- **Streamlit Docs**: https://docs.streamlit.io
- **LangChain Docs**: https://python.langchain.com
- **Groq API**: https://console.groq.com/docs
- **Docker Guide**: https://docs.docker.com

---

**Ready to deploy? Choose your option and get started! 🚀**
