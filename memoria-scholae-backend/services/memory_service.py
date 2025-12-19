"""
MemMachine integration service for persistent memory management.
"""
import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from config.settings import settings

logger = logging.getLogger(__name__)

# --- Mock Implementation for Sandbox Environment ---
class MockMemoryService:
    """Mock Service for interacting with MemMachine memory layer when not available."""
    
    def __init__(self):
        logger.warning("--- MOCKING MEMMACHINE SERVICE: External MemMachine not available. Functionality will be limited. ---")
        self.mock_memories = {}
    
    def _store_mock_memory(self, user_id: str, memory_data: Dict) -> Dict:
        if user_id not in self.mock_memories:
            self.mock_memories[user_id] = []
        memory_data["id"] = len(self.mock_memories[user_id]) + 1
        self.mock_memories[user_id].append(memory_data)
        return {"id": memory_data["id"], "status": "success"}

    def store_paper_memory(self, researcher_id: str, paper_id: str, paper_data: Dict[str, Any]) -> Dict:
        logger.info(f"Mock: Stored paper memory for {paper_id}")
        memory_data = {
            "user_id": researcher_id,
            "memory_type": "personal",
            "content": {
                "type": "paper_reading",
                "paper_id": paper_id,
                "title": paper_data.get("title"),
                "abstract": paper_data.get("abstract"),
                "key_concepts": paper_data.get("concepts", []),
                "timestamp": datetime.now().isoformat(),
                "full_content": paper_data.get("full_text", "")[:100] # Truncate for mock
            },
            "metadata": {"source": "pdf_upload"}
        }
        return self._store_mock_memory(researcher_id, memory_data)
    
    def store_annotation(self, researcher_id: str, paper_id: str, annotation: str, annotation_type: str = "note") -> Dict:
        logger.info(f"Mock: Stored annotation for {paper_id}")
        memory_data = {
            "user_id": researcher_id,
            "memory_type": "personal",
            "content": {
                "type": "annotation",
                "paper_id": paper_id,
                "annotation": annotation,
                "annotation_type": annotation_type,
                "timestamp": datetime.now().isoformat()
            },
            "metadata": {"source": "user_annotation"}
        }
        return self._store_mock_memory(researcher_id, memory_data)
    
    def recall_paper_memories(self, researcher_id: str, paper_id: Optional[str] = None, limit: int = 10) -> List[Dict]:
        logger.info(f"Mock: Recalling memories for {researcher_id}")
        memories = self.mock_memories.get(researcher_id, [])
        if paper_id:
            memories = [m for m in memories if m.get("content", {}).get("paper_id") == paper_id]
        return memories[:limit]
    
    def search_memories(self, researcher_id: str, query: str, limit: int = 10) -> List[Dict]:
        logger.info(f"Mock: Searching memories for query: {query}")
        # Return a mock search result
        return [
            {"id": 101, "score": 0.95, "content": {"type": "paper_reading", "paper_id": "mock-paper-1", "title": "Mock Paper 1: Semantic Search", "abstract": "This paper discusses semantic search.", "key_concepts": ["Semantic Search", "Vector Databases"]}},
            {"id": 102, "score": 0.88, "content": {"type": "paper_reading", "paper_id": "mock-paper-2", "title": "Mock Paper 2: Graph Reasoning", "abstract": "This paper discusses graph reasoning.", "key_concepts": ["Neo4j", "Cypher"]}}
        ][:limit]
    
    def store_hypothesis(self, researcher_id: str, hypothesis: str, supporting_papers: List[str], confidence: float) -> Dict:
        logger.info(f"Mock: Stored hypothesis for {researcher_id}")
        return {"id": 201, "status": "success"}
    
    def get_researcher_profile(self, researcher_id: str) -> Dict:
        logger.info(f"Mock: Getting profile for {researcher_id}")
        return {"name": "Mock Researcher", "interests": ["AI Agents", "Memory"]}
    
    def update_reading_history(self, researcher_id: str, paper_id: str, time_spent: int, comprehension_level: str = "medium") -> Dict:
        logger.info(f"Mock: Updated reading history for {paper_id}")
        return {"id": 301, "status": "success"}
    
    def get_recent_context(self, researcher_id: str, hours: int = 24) -> List[Dict]:
        logger.info(f"Mock: Getting recent context for {researcher_id}")
        return [
            {"id": 401, "content": {"type": "paper_reading", "paper_id": "mock-paper-1", "title": "Mock Paper 1"}},
            {"id": 402, "content": {"type": "annotation", "paper_id": "mock-paper-1", "annotation": "Key finding noted."}}
        ]

# Global instance - Use MockMemoryService
memory_service = MockMemoryService()
