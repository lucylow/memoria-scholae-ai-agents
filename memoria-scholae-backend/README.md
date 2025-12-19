# MemoriaScholae Backend

**Academic Research Assistant with MemMachine and Neo4j**

MemoriaScholae (Latin for "Memory of Learning") is an AI-powered academic research assistant that helps researchers track literature, connect ideas, and generate hypotheses. It combines **MemMachine's persistent memory layer** with **Neo4j's graph database** to create a living knowledge ecosystem that remembers everything you've read and discovers connections you might miss.

## Features

### Core Capabilities

**Persistent Memory (MemMachine)**
- Store complete reading history with annotations
- Recall past papers and insights on demand
- Track comprehension levels and time spent
- Build evolving researcher profiles

**Knowledge Graph (Neo4j)**
- Connect papers, authors, concepts, and methodologies
- Multi-hop relationship discovery
- Find bridge concepts between research areas
- Identify emerging trends and potential collaborators

**AI-Powered Intelligence (LLM)**
- Extract key concepts from papers automatically
- Generate novel research hypotheses
- Answer natural language queries about your research
- Explain complex connections between concepts

### Key Features

1. **PDF Paper Ingestion** - Upload academic papers and automatically extract metadata, concepts, and key findings
2. **Memory-Powered Recall** - Ask "What did I think about paper X?" and get your annotations and reading history
3. **Hypothesis Generation** - Generate novel, testable hypotheses based on patterns across papers
4. **Connection Discovery** - Find non-obvious connections between research concepts
5. **Literature Review Assistant** - Query your entire reading history with natural language
6. **Collaboration Suggestions** - Discover potential collaborators based on shared interests

## Architecture

```
MemoriaScholae Backend
├── FastAPI Server (main.py)
├── MemMachine Integration (services/memory_service.py)
├── Neo4j Integration (services/graph_service.py)
├── PDF Processing (services/pdf_processor.py)
├── LLM Service (services/llm_service.py)
└── Data Models (models/schemas.py)
```

### Tech Stack

- **Framework**: FastAPI (Python)
- **Memory Layer**: MemMachine (REST API)
- **Graph Database**: Neo4j (Python Driver)
- **LLM**: OpenAI API
- **PDF Processing**: PyPDF2, pdfplumber
- **Text Processing**: sentence-transformers

## Prerequisites

### Required Services

1. **MemMachine** - Memory layer for AI agents
   - Install: `docker pull memmachine/memmachine`
   - Or run from source: https://github.com/MemMachine/MemMachine
   - Default URL: `http://localhost:8080`

2. **Neo4j** - Graph database
   - Option 1: Neo4j Aura (cloud) - https://neo4j.com/
   - Option 2: Local Docker - `docker run -p 7687:7687 -p 7474:7474 neo4j`
   - Default URI: `neo4j://localhost:7687`

3. **OpenAI API Key**
   - Get from: https://platform.openai.com/api-keys
   - Or use compatible API (see configuration)

### System Requirements

- Python 3.11+
- 4GB+ RAM
- 2GB+ disk space

## Installation

### 1. Clone or Extract Backend Code

```bash
cd memoria-scholae-backend
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# MemMachine Configuration
MEMMACHINE_URL=http://localhost:8080
MEMMACHINE_API_KEY=your_api_key_if_needed

# Neo4j Configuration
NEO4J_URI=neo4j://localhost:7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=your_password
NEO4J_DATABASE=neo4j

# OpenAI Configuration
OPENAI_API_KEY=your_openai_api_key
OPENAI_MODEL=gpt-4.1-mini

# Server Configuration
SERVER_HOST=0.0.0.0
SERVER_PORT=8000
LOG_LEVEL=INFO
```

## Running the Backend

### Start Required Services

**Start MemMachine:**
```bash
# Using Docker
docker run -p 8080:8080 memmachine/memmachine

# Or from source
cd /path/to/MemMachine
python app.py
```

**Start Neo4j:**
```bash
# Using Docker
docker run \
  -p 7474:7474 -p 7687:7687 \
  -e NEO4J_AUTH=neo4j/password \
  neo4j:latest

# Or use Neo4j Desktop/Aura
```

### Start Backend Server

```bash
# Development mode (with auto-reload)
python main.py

# Or using uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

The API will be available at:
- API: http://localhost:8000
- Interactive Docs: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc

## API Endpoints

### Core Endpoints

#### Upload Paper
```http
POST /api/v1/papers/upload
Content-Type: multipart/form-data

Parameters:
- file: PDF file
- researcher_id: string
- notes: string (optional)

Response:
{
  "paper_id": "uuid",
  "title": "Paper Title",
  "authors": ["Author 1", "Author 2"],
  "concepts_extracted": ["concept1", "concept2"],
  "message": "Paper processed successfully"
}
```

#### Query Research
```http
POST /api/v1/query
Content-Type: application/json

{
  "researcher_id": "researcher_001",
  "query": "What papers discuss transformers for protein folding?"
}

Response:
{
  "answer": "Based on your reading history...",
  "relevant_papers": ["paper_id_1", "paper_id_2"],
  "concepts_used": ["transformers", "protein folding"],
  "confidence": 0.85,
  "sources": [{"title": "Paper 1"}, {"title": "Paper 2"}]
}
```

#### Generate Hypotheses
```http
POST /api/v1/hypotheses/generate
Content-Type: application/json

{
  "researcher_id": "researcher_001",
  "topic": "attention mechanisms in biology",
  "num_hypotheses": 3
}

Response:
{
  "hypotheses": [
    {
      "hypothesis_text": "Applying sparse attention to protein structure prediction...",
      "supporting_papers": ["paper1", "paper2"],
      "novelty_score": 0.85,
      "confidence_score": 0.78,
      "reasoning": "Cross-domain application shows promise..."
    }
  ],
  "total_papers_analyzed": 15
}
```

#### Find Connections
```http
POST /api/v1/graph/connections
Content-Type: application/json

{
  "researcher_id": "researcher_001",
  "source_concept": "transformers",
  "target_concept": "protein folding",
  "max_hops": 5
}

Response:
{
  "paths": [
    {
      "nodes": ["transformers", "attention", "sequences", "proteins", "protein folding"],
      "relationships": ["USES", "APPLIES_TO", "MODELS", "PREDICTS"],
      "path_length": 4,
      "relevance_score": 0.8
    }
  ],
  "bridge_concepts": ["attention mechanisms", "sequence modeling"],
  "explanation": "Transformers connect to protein folding through..."
}
```

#### Recall Memories
```http
POST /api/v1/memories/recall
Content-Type: application/json

{
  "researcher_id": "researcher_001",
  "paper_id": "optional_paper_id"
}

Response:
{
  "memories": [
    {
      "content": {
        "type": "paper_reading",
        "title": "Paper Title",
        "timestamp": "2024-03-15T10:30:00"
      }
    }
  ],
  "total_count": 10,
  "memory_type": "personal"
}
```

### Additional Endpoints

- `GET /` - Root endpoint with API info
- `GET /health` - Health check
- `GET /api/v1/researcher/{researcher_id}/profile` - Get researcher profile
- `GET /api/v1/papers/{paper_id}` - Get paper details
- `POST /api/v1/researcher/create` - Create researcher profile

## Usage Examples

### Example 1: Upload and Process a Paper

```python
import requests

url = "http://localhost:8000/api/v1/papers/upload"

with open("paper.pdf", "rb") as f:
    files = {"file": f}
    data = {
        "researcher_id": "alice_researcher",
        "notes": "Important for my thesis on attention mechanisms"
    }
    response = requests.post(url, files=files, data=data)
    print(response.json())
```

### Example 2: Query Your Research

```python
import requests

url = "http://localhost:8000/api/v1/query"

payload = {
    "researcher_id": "alice_researcher",
    "query": "What are the key findings about attention mechanisms in the papers I've read?"
}

response = requests.post(url, json=payload)
print(response.json()["answer"])
```

### Example 3: Generate Hypotheses

```python
import requests

url = "http://localhost:8000/api/v1/hypotheses/generate"

payload = {
    "researcher_id": "alice_researcher",
    "topic": "cross-attention for multi-modal learning",
    "num_hypotheses": 3
}

response = requests.post(url, json=payload)
for hypothesis in response.json()["hypotheses"]:
    print(f"Hypothesis: {hypothesis['hypothesis_text']}")
    print(f"Novelty: {hypothesis['novelty_score']}")
    print()
```

## Development

### Project Structure

```
memoria-scholae-backend/
├── main.py                      # FastAPI application
├── requirements.txt             # Python dependencies
├── .env.example                 # Environment variables template
├── README.md                    # This file
├── config/
│   └── settings.py              # Configuration management
├── models/
│   └── schemas.py               # Pydantic data models
├── services/
│   ├── memory_service.py        # MemMachine integration
│   ├── graph_service.py         # Neo4j integration
│   ├── pdf_processor.py         # PDF processing
│   └── llm_service.py           # LLM integration
├── utils/                       # Utility functions
└── tests/                       # Unit tests
```

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black .
```

## Configuration

### MemMachine Configuration

The backend connects to MemMachine via REST API. Ensure MemMachine is running and accessible at the configured URL.

**Memory Types Used:**
- `personal` - Researcher's reading history and annotations
- `project` - Research projects and hypotheses
- `working` - Current session context
- `institutional` - Cross-researcher patterns (future)

### Neo4j Configuration

The backend uses the Neo4j Python driver to interact with the graph database.

**Graph Schema:**
```
(Paper)-[:AUTHORED_BY]->(Author)
(Paper)-[:DISCUSSES]->(Concept)
(Paper)-[:CITES]->(Paper)
(Researcher)-[:READ]->(Paper)
(Researcher)-[:INTERESTED_IN]->(Concept)
```

### OpenAI Configuration

The backend uses OpenAI's API for:
- Concept extraction from papers
- Hypothesis generation
- Query answering
- Connection explanation

**Compatible Models:**
- `gpt-4.1-mini` (default, cost-effective)
- `gpt-4.1-nano` (faster, cheaper)
- `gemini-2.5-flash` (Google's model)

To use a different OpenAI-compatible API, set the base URL in the code or use environment variables.

## Troubleshooting

### MemMachine Connection Issues

```bash
# Check if MemMachine is running
curl http://localhost:8080/health

# Check logs
docker logs <memmachine_container_id>
```

### Neo4j Connection Issues

```bash
# Test Neo4j connection
cypher-shell -u neo4j -p password

# Check Neo4j status
docker logs <neo4j_container_id>
```

### PDF Processing Errors

If PDF processing fails, ensure the PDF is not encrypted or corrupted. The backend tries multiple extraction methods.

### LLM API Errors

- Check your API key is valid
- Ensure you have sufficient credits
- Check rate limits

## Performance Optimization

### For Large Paper Collections

1. **Batch Processing**: Process multiple papers in parallel
2. **Caching**: Cache LLM responses for common queries
3. **Indexing**: Ensure Neo4j indexes are created (done automatically)
4. **Memory Limits**: Configure MemMachine memory limits

### Recommended Settings

```env
# For production
LOG_LEVEL=WARNING
MAX_UPLOAD_SIZE=52428800  # 50MB
```

## Security Considerations

1. **API Keys**: Never commit `.env` file to version control
2. **CORS**: Configure allowed origins in production
3. **Authentication**: Add authentication middleware for production
4. **Rate Limiting**: Implement rate limiting for API endpoints
5. **Input Validation**: All inputs are validated via Pydantic models

## Future Enhancements

### Planned Features

- [ ] Multi-user collaboration support
- [ ] Real-time graph visualization
- [ ] Citation network analysis
- [ ] Automated literature review generation
- [ ] Integration with reference managers (Zotero, Mendeley)
- [ ] Grant proposal assistant
- [ ] Peer review helper
- [ ] Conference recommendation system

### Integration Opportunities

- LangChain for advanced agent workflows
- Streamlit frontend for visualization
- Slack/Discord integration for notifications
- Email alerts for new relevant papers

## Contributing

This is a hackathon project for the AI Agents Hackathon: Memories That Last. Contributions are welcome!

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - See LICENSE file for details

## Acknowledgments

- **MemVerge** for MemMachine - the persistent memory layer
- **Neo4j** for the graph database platform
- **OpenAI** for LLM capabilities
- **AI Agents Hackathon** for the inspiration

## Support

For issues and questions:
- GitHub Issues: [Create an issue]
- Documentation: [Read the docs]
- Community: [Join Discord]

## Citation

If you use MemoriaScholae in your research, please cite:

```bibtex
@software{memoriascholae2024,
  title={MemoriaScholae: Academic Research Assistant with Memory and Graph Intelligence},
  author={Your Name},
  year={2024},
  url={https://github.com/yourusername/memoria-scholae}
}
```

---

**Built with ❤️ for researchers who never forget**
