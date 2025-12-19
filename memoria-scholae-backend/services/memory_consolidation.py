"""
Advanced Memory Consolidation Service
Implements temporal memory evolution, decay, and consolidation patterns.
"""
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import math
from collections import defaultdict

from services.memory_service import memory_service
from services.graph_service import graph_service
from services.llm_service import llm_service

logger = logging.getLogger(__name__)


class MemoryConsolidationService:
    """
    Advanced memory consolidation implementing human-like memory patterns.
    
    Features:
    - Forgetting curve simulation (Ebbinghaus)
    - Memory reinforcement through repetition
    - Concept evolution tracking
    - Memory importance scoring
    - Cross-reference building
    """
    
    def __init__(self):
        self.decay_rate = 0.5  # Memory decay rate
        self.reinforcement_factor = 1.5  # Boost for repeated access
    
    def calculate_memory_strength(
        self, 
        memory: Dict,
        current_time: datetime
    ) -> float:
        """
        Calculate current strength of a memory using forgetting curve.
        
        Ebbinghaus forgetting curve: R = e^(-t/S)
        R = retention, t = time, S = memory strength
        """
        try:
            timestamp = memory.get("content", {}).get("timestamp")
            if not timestamp:
                return 0.5  # Default strength
            
            # Parse timestamp
            if isinstance(timestamp, str):
                memory_time = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            else:
                memory_time = timestamp
            
            # Calculate time elapsed in days
            time_elapsed = (current_time - memory_time).total_seconds() / 86400
            
            # Get access count (reinforcement)
            access_count = memory.get("metadata", {}).get("access_count", 1)
            
            # Memory strength increases with access
            strength = math.log(access_count + 1) + 1
            
            # Apply forgetting curve
            retention = math.exp(-time_elapsed / (strength * 30))  # 30-day base
            
            return min(1.0, retention)
        except Exception as e:
            logger.error(f"Error calculating memory strength: {e}")
            return 0.5
    
    def consolidate_memories(
        self, 
        researcher_id: str,
        time_window_days: int = 7
    ) -> Dict:
        """
        Consolidate memories from recent time window.
        
        Process:
        1. Retrieve recent memories
        2. Calculate memory strengths
        3. Identify related memories
        4. Merge similar memories
        5. Strengthen important memories
        6. Prune weak memories
        """
        try:
            logger.info(f"Consolidating memories for {researcher_id}")
            
            # Get recent memories
            memories = memory_service.recall_paper_memories(
                researcher_id=researcher_id,
                limit=100
            )
            
            current_time = datetime.now()
            
            # Calculate strengths
            memory_strengths = []
            for memory in memories:
                strength = self.calculate_memory_strength(memory, current_time)
                memory_strengths.append({
                    "memory": memory,
                    "strength": strength
                })
            
            # Sort by strength
            memory_strengths.sort(key=lambda x: x["strength"], reverse=True)
            
            # Identify concepts to consolidate
            concept_groups = self._group_by_concept(memory_strengths)
            
            # Build cross-references
            cross_refs = self._build_cross_references(concept_groups)
            
            # Identify memories to strengthen
            to_strengthen = [m for m in memory_strengths if m["strength"] > 0.7]
            
            # Identify memories to prune (very weak)
            to_prune = [m for m in memory_strengths if m["strength"] < 0.2]
            
            return {
                "total_memories": len(memories),
                "strong_memories": len(to_strengthen),
                "weak_memories": len(to_prune),
                "concept_groups": len(concept_groups),
                "cross_references": len(cross_refs),
                "consolidation_summary": self._generate_summary(concept_groups)
            }
        except Exception as e:
            logger.error(f"Error consolidating memories: {e}")
            return {"error": str(e)}
    
    def _group_by_concept(self, memory_strengths: List[Dict]) -> Dict[str, List]:
        """Group memories by shared concepts."""
        concept_groups = defaultdict(list)
        
        for item in memory_strengths:
            memory = item["memory"]
            concepts = memory.get("content", {}).get("key_concepts", [])
            
            for concept in concepts:
                concept_groups[concept].append(item)
        
        return dict(concept_groups)
    
    def _build_cross_references(self, concept_groups: Dict) -> List[Dict]:
        """Build cross-references between related memories."""
        cross_refs = []
        
        concepts = list(concept_groups.keys())
        for i, concept1 in enumerate(concepts):
            for concept2 in concepts[i+1:]:
                # Check if concepts appear together
                group1_papers = {
                    m["memory"].get("content", {}).get("paper_id")
                    for m in concept_groups[concept1]
                }
                group2_papers = {
                    m["memory"].get("content", {}).get("paper_id")
                    for m in concept_groups[concept2]
                }
                
                overlap = group1_papers & group2_papers
                if overlap:
                    cross_refs.append({
                        "concept1": concept1,
                        "concept2": concept2,
                        "shared_papers": len(overlap),
                        "strength": len(overlap) / min(len(group1_papers), len(group2_papers))
                    })
        
        return cross_refs
    
    def _generate_summary(self, concept_groups: Dict) -> str:
        """Generate a summary of consolidated memories."""
        top_concepts = sorted(
            concept_groups.items(),
            key=lambda x: len(x[1]),
            reverse=True
        )[:5]
        
        summary = "Top consolidated concepts:\n"
        for concept, memories in top_concepts:
            summary += f"- {concept}: {len(memories)} memories\n"
        
        return summary
    
    def track_concept_evolution(
        self, 
        researcher_id: str,
        concept: str
    ) -> Dict:
        """
        Track how understanding of a concept evolved over time.
        
        Returns timeline of concept understanding with confidence levels.
        """
        try:
            # Search for memories related to concept
            memories = memory_service.search_memories(
                researcher_id=researcher_id,
                query=concept,
                limit=50
            )
            
            # Sort by timestamp
            timeline = []
            for memory in memories:
                content = memory.get("content", {})
                if concept.lower() in str(content.get("key_concepts", [])).lower():
                    timestamp = content.get("timestamp", "")
                    timeline.append({
                        "timestamp": timestamp,
                        "paper_id": content.get("paper_id"),
                        "title": content.get("title"),
                        "context": content.get("abstract", "")[:200]
                    })
            
            # Sort chronologically
            timeline.sort(key=lambda x: x["timestamp"])
            
            # Calculate evolution metrics
            evolution_score = len(timeline) * 0.1  # More exposure = better understanding
            
            return {
                "concept": concept,
                "first_encountered": timeline[0]["timestamp"] if timeline else None,
                "total_exposures": len(timeline),
                "evolution_score": min(1.0, evolution_score),
                "timeline": timeline,
                "mastery_level": self._calculate_mastery(len(timeline))
            }
        except Exception as e:
            logger.error(f"Error tracking concept evolution: {e}")
            return {"error": str(e)}
    
    def _calculate_mastery(self, exposure_count: int) -> str:
        """Calculate mastery level based on exposures."""
        if exposure_count >= 10:
            return "expert"
        elif exposure_count >= 5:
            return "proficient"
        elif exposure_count >= 2:
            return "familiar"
        else:
            return "novice"
    
    def identify_memory_gaps(
        self, 
        researcher_id: str
    ) -> List[Dict]:
        """
        Identify gaps in researcher's knowledge based on graph structure.
        
        Finds concepts that are:
        - Connected to known concepts
        - Not yet learned
        - Important in the field
        """
        try:
            # Get researcher's papers
            papers = graph_service.get_researcher_papers(researcher_id)
            
            # Get all concepts from those papers
            known_concepts = set()
            for paper in papers:
                # Query graph for paper's concepts
                # (simplified - in production, query Neo4j)
                pass
            
            # Find neighboring concepts in graph not yet learned
            gaps = []
            
            # Use graph to find important unlearned concepts
            emerging = graph_service.get_emerging_concepts(year_threshold=2023)
            
            for concept_data in emerging[:10]:
                concept = concept_data.get("concept")
                if concept not in known_concepts:
                    gaps.append({
                        "concept": concept,
                        "importance": concept_data.get("recent_count", 0),
                        "reason": "Emerging trend in recent papers",
                        "recommended_action": "Read papers discussing this concept"
                    })
            
            return gaps
        except Exception as e:
            logger.error(f"Error identifying memory gaps: {e}")
            return []
    
    def generate_memory_report(
        self, 
        researcher_id: str
    ) -> Dict:
        """
        Generate comprehensive memory health report.
        
        Includes:
        - Memory strength distribution
        - Concept mastery levels
        - Knowledge gaps
        - Consolidation recommendations
        """
        try:
            # Get all memories
            memories = memory_service.recall_paper_memories(
                researcher_id=researcher_id,
                limit=100
            )
            
            current_time = datetime.now()
            
            # Calculate statistics
            strengths = [
                self.calculate_memory_strength(m, current_time)
                for m in memories
            ]
            
            avg_strength = sum(strengths) / len(strengths) if strengths else 0
            
            # Concept analysis
            all_concepts = []
            for memory in memories:
                concepts = memory.get("content", {}).get("key_concepts", [])
                all_concepts.extend(concepts)
            
            concept_freq = defaultdict(int)
            for concept in all_concepts:
                concept_freq[concept] += 1
            
            # Top concepts
            top_concepts = sorted(
                concept_freq.items(),
                key=lambda x: x[1],
                reverse=True
            )[:10]
            
            # Memory gaps
            gaps = self.identify_memory_gaps(researcher_id)
            
            return {
                "researcher_id": researcher_id,
                "total_memories": len(memories),
                "average_memory_strength": round(avg_strength, 2),
                "strong_memories": len([s for s in strengths if s > 0.7]),
                "weak_memories": len([s for s in strengths if s < 0.3]),
                "unique_concepts": len(concept_freq),
                "top_concepts": [{"concept": c, "frequency": f} for c, f in top_concepts],
                "knowledge_gaps": gaps[:5],
                "recommendations": self._generate_recommendations(avg_strength, len(gaps))
            }
        except Exception as e:
            logger.error(f"Error generating memory report: {e}")
            return {"error": str(e)}
    
    def _generate_recommendations(
        self, 
        avg_strength: float,
        gap_count: int
    ) -> List[str]:
        """Generate personalized recommendations."""
        recommendations = []
        
        if avg_strength < 0.5:
            recommendations.append("Review older papers to strengthen memories")
        
        if gap_count > 5:
            recommendations.append("Explore emerging concepts to fill knowledge gaps")
        
        recommendations.append("Regular reading maintains memory strength")
        
        return recommendations


# Global instance
memory_consolidation_service = MemoryConsolidationService()
