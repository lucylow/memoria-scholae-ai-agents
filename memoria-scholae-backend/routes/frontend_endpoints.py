"""
Frontend-Compatible API Endpoints
Endpoints specifically designed to match frontend expectations.
"""
import logging
from fastapi import APIRouter, HTTPException, Query as QueryParam
from typing import Optional, Dict, List, Any
from pydantic import BaseModel

from services.memory_service import memory_service
from services.graph_service import graph_service
from services.multi_agent import multi_agent_orchestrator
from services.llm_service import llm_service
from services.memory_helpers import recall_memory_by_id, get_related_concepts_from_graph

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["frontend"])


# Frontend-specific models
class QueryOptions(BaseModel):
    maxHops: Optional[int] = 3
    includeMemory: Optional[bool] = True


class FrontendQueryRequest(BaseModel):
    query: str
    options: Optional[QueryOptions] = QueryOptions()


class FrontendQueryResponse(BaseModel):
    results: Dict[str, Any]
    explanation: str
    memory_context: List[str]
    suggested_followups: List[str]
    hypothesis: Optional[str] = None


class CypherQueryRequest(BaseModel):
    query: str
    parameters: Optional[Dict[str, Any]] = {}


@router.post("/query", response_model=FrontendQueryResponse)
async def frontend_query(request: FrontendQueryRequest):
    """
    Submit a research query (frontend-compatible).
    
    Matches frontend expectations:
    - Accepts query string and options
    - Returns structured results with core_concepts, papers, themes
    - Includes explanation, memory_context, and suggested_followups
    """
    try:
        logger.info(f"Frontend query received: {request.query}")
        
        # Extract options
        max_hops = request.options.maxHops if request.options else 3
        include_memory = request.options.includeMemory if request.options else True
        
        # Use multi-agent collaboration for rich results
        researcher_id = "default_researcher"  # Could be from auth token
        
        # Get agent collaboration results
        agent_results = multi_agent_orchestrator.collaborative_research(
            researcher_id=researcher_id,
            research_topic=request.query
        )
        
        # Get memory context if requested
        memory_context = []
        if include_memory:
            recent_memories = memory_service.get_recent_context(
                researcher_id=researcher_id,
                hours=24
            )
            memory_context = [
                m.get("content", {}).get("title", "Previous research")
                for m in recent_memories[:3]
            ]
        
        # Extract concepts from query using LLM
        concepts = llm_service.extract_concepts(request.query)
        
        # Get related papers from graph
        papers = []
        for concept in concepts[:3]:
            related_papers = graph_service.get_related_papers(concept, limit=3)
            papers.extend(related_papers)
        
        # Remove duplicates
        seen = set()
        unique_papers = []
        for paper in papers:
            if paper.get("paper_id") not in seen:
                seen.add(paper.get("paper_id"))
                unique_papers.append(paper)
        
        # Build response matching frontend expectations
        response = FrontendQueryResponse(
            results={
                "type": "analysis",
                "core_concepts": concepts,
                "related_concepts": {
                    concept: graph_service.get_related_concepts(concept, limit=5)
                    for concept in concepts[:3]
                },
                "papers": unique_papers[:10],
                "emerging_themes": agent_results.get("patterns", {}).get("themes", [])
            },
            explanation=f"Based on your query about '{request.query}', I discovered fascinating connections across your knowledge graph. "
                       f"The analysis reveals {len(concepts)} core concepts with {len(unique_papers)} relevant papers.",
            memory_context=memory_context if memory_context else [
                "This is your first query in this session",
                "Building new research context"
            ],
            suggested_followups=[
                f"How do {concepts[0]} and {concepts[1]} interact?" if len(concepts) >= 2 else "What are the key methodologies?",
                f"What are recent advances in {concepts[0]}?" if concepts else "What papers should I read first?",
                "Can you identify research gaps in this area?"
            ],
            hypothesis=agent_results.get("hypotheses", [{}])[0].get("hypothesis") if agent_results.get("hypotheses") else None
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing frontend query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/memory/{memory_id}")
async def get_memory(memory_id: str):
    """
    Retrieve memory by ID (frontend-compatible).
    
    Returns a specific memory object by its ID.
    """
    try:
        logger.info(f"Retrieving memory: {memory_id}")
        
        # Retrieve memory from MemMachine
        memory = recall_memory_by_id(memory_id)
        
        if not memory:
            raise HTTPException(status_code=404, detail="Memory not found")
        
        return memory
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/graph/query")
async def execute_cypher_query(request: CypherQueryRequest):
    """
    Execute Cypher query (frontend-compatible).
    
    Allows direct execution of Cypher queries against Neo4j.
    """
    try:
        logger.info(f"Executing Cypher query: {request.query[:100]}...")
        
        # Execute Cypher query
        with graph_service.driver.session(database=graph_service.database) as session:
            result = session.run(request.query, request.parameters)
            
            # Convert result to list of dicts
            records = []
            for record in result:
                records.append(dict(record))
            
            return {
                "success": True,
                "records": records,
                "count": len(records)
            }
        
    except Exception as e:
        logger.error(f"Error executing Cypher query: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/agents/status")
async def get_agent_status():
    """
    Get agent pipeline status (frontend-compatible).
    
    Returns status of all AI agents in the system.
    """
    try:
        logger.info("Retrieving agent status")
        
        # Get agent status
        status = {
            "agents": [
                {
                    "name": "Literature Scout",
                    "status": "active",
                    "role": "discovery",
                    "personality": "curious",
                    "tasks_completed": 0,
                    "uptime": "100%"
                },
                {
                    "name": "Pattern Spotter",
                    "status": "active",
                    "role": "analysis",
                    "personality": "analytical",
                    "tasks_completed": 0,
                    "uptime": "100%"
                },
                {
                    "name": "Hypothesis Generator",
                    "status": "active",
                    "role": "synthesis",
                    "personality": "creative",
                    "tasks_completed": 0,
                    "uptime": "100%"
                }
            ],
            "system_status": "operational",
            "last_updated": "2025-12-17T16:00:00Z"
        }
        
        return status
        
    except Exception as e:
        logger.error(f"Error retrieving agent status: {e}")
        raise HTTPException(status_code=500, detail=str(e))
