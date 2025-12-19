"""
MemoriaScholae - Academic Research Assistant Backend
Main FastAPI application with MemMachine and Neo4j integration.
"""
from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging
import uuid
from io import BytesIO
from typing import List, Optional

from config.settings import settings
from models.schemas import (
    PaperUploadRequest, PaperUploadResponse,
    ResearchQuery, QueryResponse,
    MemoryRecallRequest, MemoryRecallResponse,
    HypothesisGenerationRequest, HypothesisGenerationResponse,
    GraphConnectionRequest, GraphConnectionResponse,
    ResearcherProfile, Annotation, GraphPath, Hypothesis
)
from services.memory_service import memory_service
from services.graph_service import graph_service
from services.pdf_processor import pdf_processor
from services.llm_service import llm_service
from services.memory_consolidation import memory_consolidation_service
from services.graph_reasoning import graph_reasoning_service
from services.multi_agent import multi_agent_orchestrator
from services.memory_graph_fusion import memory_graph_fusion_service
from routes.frontend_endpoints import router as frontend_router

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="MemoriaScholae API",
    description="Academic Research Assistant with MemMachine and Neo4j",
    version="1.0.0"
)

# Add CORS middleware for frontend compatibility
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  # Vite default
        "http://localhost:3000",
        "https://*.lovable.dev",
        "*"  # Allow all for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Include frontend-compatible routes
app.include_router(frontend_router)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup."""
    logger.info("Starting MemoriaScholae backend...")
    logger.info(f"MemMachine URL: {settings.memmachine_url}")
    logger.info(f"Neo4j URI: {settings.neo4j_uri}")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    logger.info("Shutting down MemoriaScholae backend...")
    graph_service.close()


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": "MemoriaScholae",
        "description": "Academic Research Assistant API",
        "version": "1.0.0",
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "memmachine": settings.memmachine_url,
        "neo4j": settings.neo4j_uri
    }


@app.post("/api/v1/papers/upload", response_model=PaperUploadResponse)
async def upload_paper(
    file: UploadFile = File(...),
    researcher_id: str = "default_researcher",
    notes: Optional[str] = None
):
    """
    Upload and process an academic paper PDF.
    
    This endpoint:
    1. Extracts text and metadata from PDF
    2. Uses LLM to extract key concepts
    3. Stores paper in MemMachine memory
    4. Creates nodes and relationships in Neo4j graph
    """
    try:
        logger.info(f"Processing paper upload from researcher: {researcher_id}")
        
        # Read PDF file
        pdf_content = await file.read()
        pdf_file = BytesIO(pdf_content)
        
        # Process PDF
        result = pdf_processor.process_pdf(pdf_file)
        
        if not result.get("success"):
            raise HTTPException(status_code=400, detail=f"PDF processing failed: {result.get('error')}")
        
        # Generate paper ID
        paper_id = str(uuid.uuid4())
        
        # Extract metadata
        metadata = result["metadata"]
        title = metadata.get("title", "Untitled")
        authors = metadata.get("authors", [])
        abstract = metadata.get("abstract", "")
        year = metadata.get("year")
        
        # Extract concepts using LLM
        full_text = result["full_text"]
        concepts = llm_service.extract_concepts(full_text)
        
        # Extract key findings
        findings = llm_service.identify_key_findings(full_text)
        
        # Store in MemMachine
        paper_data = {
            "title": title,
            "authors": authors,
            "abstract": abstract,
            "year": year,
            "concepts": concepts,
            "findings": findings,
            "full_text": full_text[:10000],  # Store first 10k chars
            "sections": result.get("sections", {}),
            "references": result.get("references", [])
        }
        
        memory_service.store_paper_memory(researcher_id, paper_id, paper_data)
        
        if notes:
            memory_service.store_annotation(researcher_id, paper_id, notes)
        
        # Store in Neo4j graph
        graph_service.create_paper_node(
            paper_id=paper_id,
            title=title,
            authors=authors,
            abstract=abstract,
            year=year
        )
        
        # Create concept nodes
        graph_service.create_concept_nodes(paper_id, concepts)
        
        # Create researcher reading relationship
        graph_service.create_reading_relationship(researcher_id, paper_id, notes)
        
        logger.info(f"Successfully processed paper: {paper_id}")
        
        return PaperUploadResponse(
            paper_id=paper_id,
            title=title,
            authors=authors,
            concepts_extracted=concepts,
            message=f"Paper processed successfully. Extracted {len(concepts)} concepts."
        )
    
    except Exception as e:
        logger.error(f"Error uploading paper: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/query", response_model=QueryResponse)
async def query_research(query: ResearchQuery):
    """
    Answer a natural language research query.
    
    Uses MemMachine to recall relevant papers and Neo4j to find connections.
    """
    try:
        logger.info(f"Processing query from {query.researcher_id}: {query.query}")
        
        # Search memories for relevant papers
        memories = memory_service.search_memories(
            researcher_id=query.researcher_id,
            query=query.query,
            limit=10
        )
        
        # Extract paper context
        paper_context = []
        for memory in memories:
            content = memory.get("content", {})
            if content.get("type") == "paper_reading":
                paper_context.append({
                    "title": content.get("title"),
                    "content": content.get("abstract", ""),
                    "paper_id": content.get("paper_id")
                })
        
        # Get researcher context
        recent_context = memory_service.get_recent_context(query.researcher_id, hours=168)  # Last week
        
        # Use LLM to answer query
        result = llm_service.answer_query(
            query=query.query,
            context=paper_context,
            researcher_context=f"Recently read {len(recent_context)} papers"
        )
        
        return QueryResponse(
            answer=result["answer"],
            relevant_papers=[p["paper_id"] for p in paper_context],
            concepts_used=[],
            confidence=result["confidence"],
            sources=[{"title": s} for s in result["sources"]]
        )
    
    except Exception as e:
        logger.error(f"Error processing query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/memories/recall", response_model=MemoryRecallResponse)
async def recall_memories(request: MemoryRecallRequest):
    """
    Recall memories from MemMachine.
    
    Can filter by paper_id, concept, or time range.
    """
    try:
        logger.info(f"Recalling memories for {request.researcher_id}")
        
        if request.paper_id:
            memories = memory_service.recall_paper_memories(
                researcher_id=request.researcher_id,
                paper_id=request.paper_id
            )
        else:
            memories = memory_service.recall_paper_memories(
                researcher_id=request.researcher_id
            )
        
        return MemoryRecallResponse(
            memories=memories,
            total_count=len(memories),
            memory_type="personal"
        )
    
    except Exception as e:
        logger.error(f"Error recalling memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/hypotheses/generate", response_model=HypothesisGenerationResponse)
async def generate_hypotheses(request: HypothesisGenerationRequest):
    """
    Generate novel research hypotheses based on papers read.
    
    Uses Neo4j to find patterns and LLM to generate hypotheses.
    """
    try:
        logger.info(f"Generating hypotheses for {request.researcher_id} on topic: {request.topic}")
        
        # Get researcher's papers from graph
        papers = graph_service.get_researcher_papers(request.researcher_id)
        
        # Get related papers from graph
        topic_papers = graph_service.get_related_papers(request.topic, limit=20)
        
        # Combine papers
        all_papers = papers + topic_papers
        
        # Get paper details from memory
        paper_context = []
        for paper in all_papers[:15]:
            memories = memory_service.recall_paper_memories(
                researcher_id=request.researcher_id,
                paper_id=paper.get("paper_id")
            )
            if memories:
                content = memories[0].get("content", {})
                paper_context.append({
                    "title": content.get("title"),
                    "abstract": content.get("abstract"),
                    "summary": content.get("abstract", "")[:200]
                })
        
        # Generate hypotheses using LLM
        hypotheses_data = llm_service.generate_hypotheses(
            topic=request.topic,
            papers_context=paper_context,
            num_hypotheses=request.num_hypotheses
        )
        
        # Convert to Hypothesis objects
        hypotheses = []
        for h_data in hypotheses_data:
            hypothesis = Hypothesis(
                hypothesis_text=h_data.get("hypothesis_text", ""),
                supporting_papers=[p.get("title", "") for p in paper_context[:3]],
                novelty_score=h_data.get("novelty_score", 0.7),
                confidence_score=h_data.get("confidence_score", 0.7),
                reasoning=h_data.get("reasoning", "")
            )
            hypotheses.append(hypothesis)
            
            # Store hypothesis in memory
            memory_service.store_hypothesis(
                researcher_id=request.researcher_id,
                hypothesis=hypothesis.hypothesis_text,
                supporting_papers=[p.get("title", "") for p in paper_context[:3]],
                confidence=hypothesis.confidence_score
            )
        
        return HypothesisGenerationResponse(
            hypotheses=hypotheses,
            total_papers_analyzed=len(paper_context)
        )
    
    except Exception as e:
        logger.error(f"Error generating hypotheses: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/graph/connections", response_model=GraphConnectionResponse)
async def find_graph_connections(request: GraphConnectionRequest):
    """
    Find connections between concepts in the knowledge graph.
    
    Uses Neo4j to discover multi-hop relationships.
    """
    try:
        logger.info(f"Finding connections between {request.source_concept} and {request.target_concept}")
        
        # Find paths in graph
        paths_data = graph_service.find_connections(
            source_concept=request.source_concept,
            target_concept=request.target_concept,
            max_hops=request.max_hops
        )
        
        # Find bridge concepts
        bridge_concepts = graph_service.find_bridge_concepts(
            request.source_concept,
            request.target_concept
        )
        
        # Convert to GraphPath objects
        paths = []
        for path_data in paths_data:
            path = GraphPath(
                nodes=path_data["nodes"],
                relationships=path_data["relationships"],
                path_length=path_data["path_length"],
                relevance_score=1.0 / (path_data["path_length"] + 1)
            )
            paths.append(path)
        
        # Generate explanation
        if paths:
            explanation = llm_service.explain_connection(
                concept1=request.source_concept,
                concept2=request.target_concept,
                path_info=paths[0].nodes
            )
        else:
            explanation = "No direct connection found between these concepts in the current knowledge graph."
        
        return GraphConnectionResponse(
            paths=paths,
            bridge_concepts=bridge_concepts,
            explanation=explanation
        )
    
    except Exception as e:
        logger.error(f"Error finding connections: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/researcher/{researcher_id}/profile", response_model=ResearcherProfile)
async def get_researcher_profile(researcher_id: str):
    """Get researcher profile with statistics."""
    try:
        # Get papers from graph
        papers = graph_service.get_researcher_papers(researcher_id)
        
        # Get memories
        memories = memory_service.recall_paper_memories(researcher_id, limit=100)
        
        # Count concepts
        concepts = set()
        for memory in memories:
            content = memory.get("content", {})
            if "key_concepts" in content:
                concepts.update(content["key_concepts"])
        
        return ResearcherProfile(
            researcher_id=researcher_id,
            name=researcher_id,
            research_interests=[],
            papers_read=len(papers),
            concepts_learned=len(concepts),
            hypotheses_generated=0
        )
    
    except Exception as e:
        logger.error(f"Error getting researcher profile: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/papers/{paper_id}")
async def get_paper(paper_id: str, researcher_id: str):
    """Get paper details from memory and graph."""
    try:
        # Get from memory
        memories = memory_service.recall_paper_memories(
            researcher_id=researcher_id,
            paper_id=paper_id
        )
        
        if not memories:
            raise HTTPException(status_code=404, detail="Paper not found")
        
        paper_data = memories[0].get("content", {})
        
        return {
            "paper_id": paper_id,
            "title": paper_data.get("title"),
            "authors": paper_data.get("authors", []),
            "abstract": paper_data.get("abstract"),
            "concepts": paper_data.get("key_concepts", []),
            "findings": paper_data.get("findings", [])
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting paper: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/researcher/create")
async def create_researcher(researcher_id: str, name: str, interests: List[str]):
    """Create a new researcher profile."""
    try:
        graph_service.create_researcher_node(
            researcher_id=researcher_id,
            name=name,
            interests=interests
        )
        
        return {
            "researcher_id": researcher_id,
            "name": name,
            "interests": interests,
            "message": "Researcher profile created successfully"
        }
    
    except Exception as e:
        logger.error(f"Error creating researcher: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/memory/consolidate")
async def consolidate_memories(researcher_id: str, time_window_days: int = 7):
    """
    Consolidate memories with forgetting curve simulation.
    
    Advanced memory management:
    - Calculate memory strengths
    - Identify concepts to consolidate
    - Build cross-references
    - Prune weak memories
    """
    try:
        result = memory_consolidation_service.consolidate_memories(
            researcher_id=researcher_id,
            time_window_days=time_window_days
        )
        return result
    except Exception as e:
        logger.error(f"Error consolidating memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/memory/report/{researcher_id}")
async def get_memory_report(researcher_id: str):
    """
    Generate comprehensive memory health report.
    
    Includes:
    - Memory strength distribution
    - Concept mastery levels
    - Knowledge gaps
    - Personalized recommendations
    """
    try:
        report = memory_consolidation_service.generate_memory_report(researcher_id)
        return report
    except Exception as e:
        logger.error(f"Error generating memory report: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/concept/evolution/{researcher_id}/{concept}")
async def track_concept_evolution(researcher_id: str, concept: str):
    """
    Track how understanding of a concept evolved over time.
    
    Returns timeline with:
    - First encounter
    - Exposure history
    - Mastery progression
    - Evolution score
    """
    try:
        evolution = memory_consolidation_service.track_concept_evolution(
            researcher_id=researcher_id,
            concept=concept
        )
        return evolution
    except Exception as e:
        logger.error(f"Error tracking concept evolution: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/graph/analogies")
async def find_analogies(source_domain: str, target_domain: str, max_analogies: int = 5):
    """
    Find analogical patterns between research domains.
    
    Discovers:
    - Methodological similarities
    - Conceptual bridges
    - Transferable insights
    """
    try:
        analogies = graph_reasoning_service.find_analogies(
            source_domain=source_domain,
            target_domain=target_domain,
            max_analogies=max_analogies
        )
        return {"analogies": analogies}
    except Exception as e:
        logger.error(f"Error finding analogies: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/graph/contradictions/{concept}")
async def detect_contradictions(concept: str):
    """
    Detect contradictory findings in literature.
    
    Identifies:
    - Opposing conclusions
    - Conflicting methodologies
    - Unresolved debates
    """
    try:
        contradictions = graph_reasoning_service.detect_contradictions(concept)
        return {"contradictions": contradictions}
    except Exception as e:
        logger.error(f"Error detecting contradictions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/graph/gaps/{research_area}")
async def analyze_research_gaps(research_area: str):
    """
    Identify research gaps using graph structure.
    
    Finds:
    - Under-explored connections
    - Missing methodologies
    - Novel concept combinations
    """
    try:
        gaps = graph_reasoning_service.analyze_research_gaps(research_area)
        return gaps
    except Exception as e:
        logger.error(f"Error analyzing research gaps: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/graph/lifecycle/{concept}")
async def track_concept_lifecycle(concept: str):
    """
    Track concept lifecycle: birth, growth, maturity, decline.
    
    Analyzes:
    - Emergence timeline
    - Growth rate
    - Current stage
    - Future trajectory
    """
    try:
        lifecycle = graph_reasoning_service.track_concept_lifecycle(concept)
        return lifecycle
    except Exception as e:
        logger.error(f"Error tracking concept lifecycle: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/graph/influence/{paper_id}")
async def calculate_influence(paper_id: str, max_depth: int = 3):
    """
    Calculate influence propagation through citations.
    
    Measures:
    - Direct and indirect citations
    - Influence decay
    - Spread across domains
    """
    try:
        influence = graph_reasoning_service.calculate_influence_propagation(
            paper_id=paper_id,
            max_depth=max_depth
        )
        return influence
    except Exception as e:
        logger.error(f"Error calculating influence: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/graph/synthesis")
async def find_synthesis_paths(concepts: List[str]):
    """
    Find paths to synthesize multiple concepts.
    
    Identifies:
    - Common methodologies
    - Shared frameworks
    - Potential fusion points
    """
    try:
        paths = graph_reasoning_service.find_synthesis_paths(concepts)
        return {"synthesis_paths": paths}
    except Exception as e:
        logger.error(f"Error finding synthesis paths: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/graph/communities")
async def detect_communities(min_size: int = 3):
    """
    Detect research communities using graph clustering.
    
    Identifies:
    - Collaboration networks
    - Research clusters
    - Community cohesion
    """
    try:
        communities = graph_reasoning_service.detect_research_communities(min_size)
        return {"communities": communities}
    except Exception as e:
        logger.error(f"Error detecting communities: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/agents/collaborate")
async def multi_agent_collaboration(researcher_id: str, research_topic: str):
    """
    Coordinate multiple AI agents for collaborative research.
    
    Agents:
    - Literature Scout: Finds relevant papers
    - Pattern Spotter: Identifies patterns
    - Hypothesis Generator: Creates hypotheses
    
    Returns collaborative insights and refined hypotheses.
    """
    try:
        result = multi_agent_orchestrator.collaborative_research(
            researcher_id=researcher_id,
            research_topic=research_topic
        )
        return result
    except Exception as e:
        logger.error(f"Error in multi-agent collaboration: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/fusion/personalized-graph/{researcher_id}")
async def get_personalized_graph(researcher_id: str):
    """
    Create personalized knowledge graph view based on memory.
    
    Graph is filtered and weighted by:
    - Reading history
    - Memory strength
    - Comprehension levels
    - Research interests
    """
    try:
        graph_view = memory_graph_fusion_service.personalized_graph_view(researcher_id)
        return graph_view
    except Exception as e:
        logger.error(f"Error creating personalized graph: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/fusion/serendipity/{researcher_id}")
async def discover_serendipity(researcher_id: str):
    """
    Find serendipitous discoveries at intersection of knowledge.
    
    Discovers:
    - Unexpected connections
    - Cross-domain opportunities
    - Hidden patterns
    """
    try:
        discoveries = memory_graph_fusion_service.serendipitous_discovery(researcher_id)
        return {"discoveries": discoveries}
    except Exception as e:
        logger.error(f"Error finding serendipitous discoveries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/fusion/intuition")
async def get_research_intuition(researcher_id: str, current_context: str):
    """
    Generate research intuition based on memory patterns.
    
    Provides:
    - Gut feeling about directions
    - Pattern-based suggestions
    - Warnings about pitfalls
    """
    try:
        intuition = memory_graph_fusion_service.research_intuition(
            researcher_id=researcher_id,
            current_context=current_context
        )
        return intuition
    except Exception as e:
        logger.error(f"Error generating research intuition: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/v1/fusion/cognitive-load/{researcher_id}")
async def optimize_cognitive_load(researcher_id: str):
    """
    Optimize learning based on cognitive load.
    
    Recommends:
    - Reading schedule
    - Review timing
    - Break periods
    - Focus areas
    """
    try:
        optimization = memory_graph_fusion_service.cognitive_load_optimizer(researcher_id)
        return optimization
    except Exception as e:
        logger.error(f"Error optimizing cognitive load: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/v1/fusion/learning-path")
async def generate_learning_path(researcher_id: str, target_concept: str):
    """
    Generate personalized learning path using memory and graph.
    
    Creates path from current knowledge to target:
    - Assesses current knowledge
    - Finds path in graph
    - Orders by difficulty
    - Considers memory capacity
    """
    try:
        path = memory_graph_fusion_service.learning_path_generator(
            researcher_id=researcher_id,
            target_concept=target_concept
        )
        return path
    except Exception as e:
        logger.error(f"Error generating learning path: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.server_host,
        port=settings.server_port,
        reload=True,
        log_level=settings.log_level.lower()
    )
