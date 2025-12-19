"""
Memory Service Helper Functions
Additional utility functions for memory operations.
"""
import logging
from typing import Optional, Dict, Any
from services.memory_service import memory_service

logger = logging.getLogger(__name__)


def recall_memory_by_id(memory_id: str) -> Optional[Dict[str, Any]]:
    """
    Recall a specific memory by its ID.
    
    Args:
        memory_id: Unique identifier for the memory
        
    Returns:
        Memory object or None if not found
    """
    try:
        # In MemMachine, memories are stored with metadata
        # We need to search through memories to find the one with matching ID
        
        # For now, return a placeholder
        # In production, implement proper ID-based retrieval from MemMachine
        
        logger.info(f"Attempting to recall memory: {memory_id}")
        
        # Placeholder response
        return {
            "memory_id": memory_id,
            "type": "paper_reading",
            "content": {
                "title": "Memory retrieved",
                "timestamp": "2025-12-17T16:00:00Z"
            },
            "note": "Memory retrieval by ID - implement with MemMachine search"
        }
        
    except Exception as e:
        logger.error(f"Error recalling memory by ID: {e}")
        return None


def get_related_concepts_from_graph(concept: str, limit: int = 5) -> list:
    """
    Get related concepts from the knowledge graph.
    
    Args:
        concept: Source concept
        limit: Maximum number of related concepts
        
    Returns:
        List of related concept names
    """
    try:
        from services.graph_service import graph_service
        
        with graph_service.driver.session(database=graph_service.database) as session:
            query = """
            MATCH (c1:Concept {name: $concept})-[:RELATED_TO]-(c2:Concept)
            RETURN c2.name as related_concept
            LIMIT $limit
            """
            
            result = session.run(query, concept=concept, limit=limit)
            
            related = [record["related_concept"] for record in result]
            
            return related if related else []
            
    except Exception as e:
        logger.error(f"Error getting related concepts: {e}")
        return []
