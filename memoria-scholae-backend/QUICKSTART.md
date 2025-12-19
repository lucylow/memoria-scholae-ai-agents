# MemoriaScholae Backend - Quick Start Guide

Get the backend running in 5 minutes!

## Prerequisites

Before you start, make sure you have:

1. **Python 3.11+** installed
2. **Docker** installed (for MemMachine and Neo4j)
3. **OpenAI API Key** (or compatible LLM API)

## Step 1: Extract the Backend

```bash
unzip memoria-scholae-backend.zip
cd memoria-scholae-backend
```

## Step 2: Start Required Services

### Start MemMachine

```bash
docker run -d -p 8080:8080 --name memmachine memmachine/memmachine:latest
```

Verify it's running:
```bash
curl http://localhost:8080/health
```

### Start Neo4j

```bash
docker run -d \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  --name neo4j \
  neo4j:latest
```

Wait 30 seconds for Neo4j to start, then verify:
```bash
# Neo4j browser will be at http://localhost:7474
# Login: neo4j / password
```

## Step 3: Configure Environment

```bash
cp .env.example .env
```

Edit `.env` and add your OpenAI API key:
```env
OPENAI_API_KEY=sk-your-api-key-here
```

The defaults should work for local development:
```env
MEMMACHINE_URL=http://localhost:8080
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password
```

## Step 4: Install Dependencies

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## Step 5: Start the Backend

```bash
python main.py
```

Or use the quick start script:
```bash
./start.sh
```

The backend will start at **http://localhost:8000**

## Step 6: Test the API

### Option 1: Interactive Docs

Open your browser to:
- **http://localhost:8000/docs** (Swagger UI)
- **http://localhost:8000/redoc** (ReDoc)

### Option 2: Test Script

```bash
python test_api.py
```

### Option 3: Manual Test

```bash
# Health check
curl http://localhost:8000/health

# Create a researcher
curl -X POST "http://localhost:8000/api/v1/researcher/create?researcher_id=alice&name=Alice%20Researcher&interests=AI&interests=graphs"

# Test query
curl -X POST http://localhost:8000/api/v1/query \
  -H "Content-Type: application/json" \
  -d '{
    "researcher_id": "alice",
    "query": "What are the latest trends in AI?"
  }'
```

## Step 7: Upload Your First Paper

Using the interactive docs at http://localhost:8000/docs:

1. Go to **POST /api/v1/papers/upload**
2. Click "Try it out"
3. Upload a PDF file
4. Set `researcher_id` to "alice"
5. Click "Execute"

The backend will:
- Extract text and metadata
- Identify key concepts using AI
- Store in MemMachine memory
- Create nodes in Neo4j graph
- Return extracted information

## What's Next?

### Try These Features

1. **Query Your Papers**
   ```bash
   curl -X POST http://localhost:8000/api/v1/query \
     -H "Content-Type: application/json" \
     -d '{
       "researcher_id": "alice",
       "query": "Summarize the main findings from my papers"
     }'
   ```

2. **Generate Hypotheses**
   ```bash
   curl -X POST http://localhost:8000/api/v1/hypotheses/generate \
     -H "Content-Type: application/json" \
     -d '{
       "researcher_id": "alice",
       "topic": "graph neural networks",
       "num_hypotheses": 3
     }'
   ```

3. **Find Connections**
   ```bash
   curl -X POST http://localhost:8000/api/v1/graph/connections \
     -H "Content-Type: application/json" \
     -d '{
       "researcher_id": "alice",
       "source_concept": "transformers",
       "target_concept": "graph neural networks",
       "max_hops": 5
     }'
   ```

4. **Recall Memories**
   ```bash
   curl -X POST http://localhost:8000/api/v1/memories/recall \
     -H "Content-Type: application/json" \
     -d '{
       "researcher_id": "alice"
     }'
   ```

### Explore the Data

**Neo4j Browser**: http://localhost:7474
- Login: neo4j / password
- Try: `MATCH (n) RETURN n LIMIT 25`

**MemMachine**: http://localhost:8080
- Check memory storage and retrieval

## Troubleshooting

### MemMachine not running?
```bash
docker ps | grep memmachine
docker logs memmachine
```

### Neo4j not running?
```bash
docker ps | grep neo4j
docker logs neo4j
```

### Backend errors?
Check the console output for error messages. Common issues:
- Missing OpenAI API key
- MemMachine/Neo4j not accessible
- Port already in use

### Port conflicts?
Change ports in `.env`:
```env
SERVER_PORT=8001  # Instead of 8000
```

## Using Docker Compose (Alternative)

Instead of running services separately, use Docker Compose:

```bash
# Set your OpenAI API key
export OPENAI_API_KEY=sk-your-key-here

# Start everything
docker-compose up -d

# View logs
docker-compose logs -f

# Stop everything
docker-compose down
```

This starts:
- MemMachine on port 8080
- Neo4j on ports 7474 and 7687
- Backend on port 8000

## Next Steps

1. **Read the README.md** for detailed API documentation
2. **Check ARCHITECTURE.md** to understand the system design
3. **Build a frontend** to interact with the API
4. **Customize** the code for your specific needs

## Support

- Check the logs for error messages
- Review the README.md for detailed documentation
- Test individual services to isolate issues

---

**You're ready to go! Start uploading papers and discovering connections! 🚀**
