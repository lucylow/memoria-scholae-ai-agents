# MemoriaScholae Architecture

## System Overview

MemoriaScholae is a multi-agent academic research assistant that combines persistent memory (MemMachine) with graph-based reasoning (Neo4j) to help researchers manage literature, discover connections, and generate novel hypotheses.

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend (Future)                        │
│              React/Streamlit Web Interface                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   FastAPI Backend (main.py)                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ PDF Upload   │  │   Query      │  │ Hypothesis   │      │
│  │   Endpoint   │  │  Endpoint    │  │  Generator   │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│  PDF Processor  │  │  Memory Service │  │  Graph Service  │
│   (PyPDF2)      │  │  (MemMachine)   │  │    (Neo4j)      │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                    │                    │
         └────────────────────┴────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │   LLM Service   │
                    │    (OpenAI)     │
                    └─────────────────┘
```

## Core Components

### 1. FastAPI Backend (`main.py`)

**Responsibilities:**
- HTTP request handling
- Request validation
- Response formatting
- Service orchestration
- Error handling

**Key Endpoints:**
- `/api/v1/papers/upload` - Paper ingestion
- `/api/v1/query` - Natural language queries
- `/api/v1/hypotheses/generate` - Hypothesis generation
- `/api/v1/graph/connections` - Connection discovery
- `/api/v1/memories/recall` - Memory retrieval

### 2. Memory Service (`services/memory_service.py`)

**Integration with MemMachine:**

MemMachine provides a persistent memory layer that stores:
- **Personal Memory**: Individual researcher's reading history, annotations, preferences
- **Project Memory**: Research project context, hypotheses, findings
- **Working Memory**: Current session context
- **Institutional Memory**: Cross-researcher patterns (future)

**Key Operations:**
```python
# Store paper reading
memory_service.store_paper_memory(researcher_id, paper_id, paper_data)

# Recall memories
memories = memory_service.recall_paper_memories(researcher_id, paper_id)

# Search semantically
results = memory_service.search_memories(researcher_id, query)

# Store hypothesis
memory_service.store_hypothesis(researcher_id, hypothesis, papers, confidence)
```

**Memory Schema:**
```json
{
  "user_id": "researcher_001",
  "memory_type": "personal",
  "content": {
    "type": "paper_reading",
    "paper_id": "uuid",
    "title": "Paper Title",
    "key_concepts": ["concept1", "concept2"],
    "timestamp": "2024-03-15T10:30:00"
  },
  "metadata": {
    "source": "pdf_upload",
    "importance": "high"
  }
}
```

### 3. Graph Service (`services/graph_service.py`)

**Integration with Neo4j:**

Neo4j provides graph-based reasoning through:
- **Node Types**: Paper, Author, Concept, Researcher, Methodology
- **Relationship Types**: CITES, AUTHORED_BY, DISCUSSES, READ, USES_METHOD
- **Queries**: Cypher for complex graph traversal

**Graph Schema:**
```cypher
// Papers and Authors
(Paper)-[:AUTHORED_BY]->(Author)

// Papers and Concepts
(Paper)-[:DISCUSSES]->(Concept)

// Citations
(Paper)-[:CITES]->(Paper)

// Researcher Activity
(Researcher)-[:READ]->(Paper)
(Researcher)-[:INTERESTED_IN]->(Concept)

// Methodologies
(Paper)-[:USES_METHOD]->(Methodology)
```

**Key Operations:**
```python
# Create paper node
graph_service.create_paper_node(paper_id, title, authors, abstract, year)

# Create concept relationships
graph_service.create_concept_nodes(paper_id, concepts)

# Find connections
paths = graph_service.find_connections(source_concept, target_concept, max_hops)

# Find bridge concepts
bridges = graph_service.find_bridge_concepts(concept1, concept2)

# Suggest collaborators
collaborators = graph_service.suggest_collaborators(researcher_id)
```

### 4. PDF Processor (`services/pdf_processor.py`)

**Responsibilities:**
- Extract text from PDF files
- Parse metadata (title, authors, abstract, year)
- Extract sections (introduction, methods, results, etc.)
- Extract references
- Handle various PDF formats

**Processing Pipeline:**
```
PDF File → Text Extraction → Metadata Parsing → Section Detection → Output
```

**Extraction Methods:**
1. **Primary**: pdfplumber (better table/layout handling)
2. **Fallback**: PyPDF2 (broader compatibility)

### 5. LLM Service (`services/llm_service.py`)

**Integration with OpenAI:**

Uses LLM for intelligent text processing:
- **Concept Extraction**: Identify key research concepts from papers
- **Summarization**: Generate concise paper summaries
- **Query Answering**: Answer questions using context
- **Hypothesis Generation**: Create novel research hypotheses
- **Connection Explanation**: Explain graph relationships

**Key Operations:**
```python
# Extract concepts
concepts = llm_service.extract_concepts(paper_text)

# Answer query
result = llm_service.answer_query(query, context, researcher_context)

# Generate hypotheses
hypotheses = llm_service.generate_hypotheses(topic, papers_context, num=3)

# Explain connection
explanation = llm_service.explain_connection(concept1, concept2, path)
```

## Data Flow

### Paper Upload Flow

```
1. User uploads PDF
   ↓
2. PDF Processor extracts text and metadata
   ↓
3. LLM Service extracts concepts and findings
   ↓
4. Memory Service stores in MemMachine
   ↓
5. Graph Service creates nodes in Neo4j
   ↓
6. Response returned to user
```

### Query Flow

```
1. User submits natural language query
   ↓
2. Memory Service searches for relevant papers
   ↓
3. Graph Service finds related concepts
   ↓
4. LLM Service generates answer using context
   ↓
5. Response with answer and sources returned
```

### Hypothesis Generation Flow

```
1. User requests hypotheses on a topic
   ↓
2. Graph Service finds related papers
   ↓
3. Memory Service retrieves paper details
   ↓
4. LLM Service generates novel hypotheses
   ↓
5. Memory Service stores hypotheses
   ↓
6. Hypotheses with confidence scores returned
```

## Memory Layer Details

### MemMachine Integration

**Why MemMachine?**
- Persistent storage across sessions
- Semantic search capabilities
- Multi-layer memory architecture
- User-specific context preservation

**Memory Types:**

1. **Working Memory** (Current Session)
   - Active papers being read
   - Current queries
   - Temporary annotations

2. **Personal Memory** (Long-term)
   - Complete reading history
   - All annotations and notes
   - Comprehension levels
   - Time spent on papers

3. **Project Memory** (Research Projects)
   - Project-specific context
   - Generated hypotheses
   - Research goals

4. **Institutional Memory** (Cross-user)
   - Common patterns
   - Successful research strategies
   - Collaboration networks

### Memory Retrieval Strategies

1. **Exact Recall**: Get specific paper by ID
2. **Semantic Search**: Find papers by concept similarity
3. **Temporal Filtering**: Recent vs. historical memories
4. **Context-Aware**: Based on current research focus

## Graph Database Details

### Neo4j Integration

**Why Neo4j?**
- Natural representation of academic relationships
- Efficient multi-hop queries
- Pattern matching for discovery
- Scalable for large knowledge graphs

**Graph Patterns:**

1. **Citation Network**
```cypher
MATCH (p1:Paper)-[:CITES*1..3]->(p2:Paper)
WHERE p1.paper_id = $paper_id
RETURN p2
```

2. **Concept Bridges**
```cypher
MATCH (c1:Concept)<-[:DISCUSSES]-(p1:Paper)
MATCH (c2:Concept)<-[:DISCUSSES]-(p2:Paper)
MATCH (p1)-[:DISCUSSES]->(bridge:Concept)<-[:DISCUSSES]-(p2)
RETURN bridge
```

3. **Collaboration Suggestions**
```cypher
MATCH (r:Researcher)-[:READ]->(p:Paper)-[:DISCUSSES]->(c:Concept)
MATCH (c)<-[:DISCUSSES]-(p2:Paper)<-[:AUTHORED_BY]-(a:Author)
RETURN a, count(*) as relevance
ORDER BY relevance DESC
```

## API Design Principles

### RESTful Design

- Resource-based URLs
- HTTP methods (GET, POST, PUT, DELETE)
- JSON request/response
- Proper status codes

### Request/Response Format

**Request:**
```json
{
  "researcher_id": "unique_id",
  "query": "natural language query",
  "context": {}
}
```

**Response:**
```json
{
  "answer": "response text",
  "confidence": 0.85,
  "sources": [...],
  "metadata": {...}
}
```

### Error Handling

- Validation errors: 400 Bad Request
- Not found: 404 Not Found
- Server errors: 500 Internal Server Error
- Detailed error messages in response

## Security Considerations

### API Security

1. **Input Validation**: Pydantic models validate all inputs
2. **File Upload Limits**: Max 50MB per file
3. **CORS**: Configurable allowed origins
4. **Rate Limiting**: (To be implemented)
5. **Authentication**: (To be implemented)

### Data Privacy

1. **User Isolation**: Researcher IDs isolate data
2. **No Shared Memories**: Personal memories are private
3. **Secure Storage**: Environment variables for secrets
4. **No Logging of Sensitive Data**: PII excluded from logs

## Scalability Considerations

### Horizontal Scaling

- **Stateless Backend**: Can run multiple instances
- **Shared MemMachine**: Centralized memory layer
- **Shared Neo4j**: Centralized graph database
- **Load Balancer**: Distribute requests

### Performance Optimization

1. **Caching**: Cache LLM responses for common queries
2. **Batch Processing**: Process multiple papers in parallel
3. **Lazy Loading**: Load paper content on demand
4. **Graph Indexes**: Neo4j indexes on frequently queried properties
5. **Connection Pooling**: Reuse database connections

### Resource Management

- **Memory Limits**: Configure max memory per request
- **Timeout Settings**: Prevent long-running requests
- **Queue System**: For background processing (future)

## Deployment Architecture

### Docker Compose Deployment

```
┌─────────────────────────────────────────────────────────┐
│                    Docker Network                        │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
│  │  MemMachine  │  │    Neo4j     │  │   Backend    │  │
│  │  Container   │  │  Container   │  │  Container   │  │
│  │  :8080       │  │  :7687       │  │  :8000       │  │
│  └──────────────┘  └──────────────┘  └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### Production Deployment

- **Backend**: Multiple instances behind load balancer
- **MemMachine**: Clustered for high availability
- **Neo4j**: Causal cluster for read scalability
- **Monitoring**: Prometheus + Grafana
- **Logging**: ELK stack

## Future Enhancements

### Planned Features

1. **Multi-Agent Collaboration**
   - Specialized agents for different tasks
   - Agent coordination via MemMachine
   - Shared knowledge graph

2. **Real-time Updates**
   - WebSocket support
   - Live graph visualization
   - Notification system

3. **Advanced Analytics**
   - Research trend analysis
   - Impact prediction
   - Collaboration network analysis

4. **Integration Ecosystem**
   - Zotero/Mendeley connectors
   - arXiv auto-import
   - Google Scholar integration
   - Slack/Discord notifications

### Technical Improvements

1. **Caching Layer**: Redis for performance
2. **Message Queue**: RabbitMQ for async tasks
3. **Vector Database**: For better semantic search
4. **GraphQL API**: Alternative to REST
5. **gRPC**: For internal service communication

## Development Guidelines

### Code Organization

- **Separation of Concerns**: Each service has single responsibility
- **Dependency Injection**: Services injected where needed
- **Configuration Management**: Centralized in `config/settings.py`
- **Error Handling**: Consistent across all endpoints

### Testing Strategy

1. **Unit Tests**: Test individual functions
2. **Integration Tests**: Test service interactions
3. **API Tests**: Test endpoint behavior
4. **Load Tests**: Test performance under load

### Documentation

- **Code Comments**: Explain complex logic
- **Docstrings**: All functions documented
- **API Docs**: Auto-generated via FastAPI
- **Architecture Docs**: This file

## Conclusion

MemoriaScholae's architecture combines the strengths of persistent memory (MemMachine) and graph databases (Neo4j) to create a powerful research assistant. The modular design allows for easy extension and scaling, while the clear separation of concerns makes the codebase maintainable and testable.
