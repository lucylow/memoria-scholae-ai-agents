"""
Memory-Graph Fusion Service
Innovative features combining MemMachine memory and Neo4j graph reasoning.
"""
import logging
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import math

from services.memory_service import memory_service
from services.graph_service import graph_service
from services.memory_consolidation import memory_consolidation_service
from services.graph_reasoning import graph_reasoning_service

logger = logging.getLogger(__name__)


class MemoryGraphFusionService:
    """
    Fuses memory and graph capabilities for emergent intelligence.
    
    Features:
    - Memory-informed graph queries
    - Graph-enhanced memory retrieval
    - Serendipitous discovery
    - Research intuition
    - Cognitive load management
    """
    
    def __init__(self):
        pass
    
    def personalized_graph_view(
        self, 
        researcher_id: str
    ) -> Dict:
        """
        Create a personalized view of the knowledge graph based on memory.
        
        The graph is filtered and weighted by:
        - What the researcher has read
        - Memory strength of concepts
        - Comprehension levels
        - Research interests
        """
        try:
            logger.info(f"Creating personalized graph view for {researcher_id}")
            
            # Get researcher's memories
            memories = memory_service.recall_paper_memories(
                researcher_id=researcher_id,
                limit=50
            )
            
            # Extract concepts with memory strengths
            concept_strengths = {}
            current_time = datetime.now()
            
            for memory in memories:
                concepts = memory.get("content", {}).get("key_concepts", [])
                strength = memory_consolidation_service.calculate_memory_strength(
                    memory, current_time
                )
                
                for concept in concepts:
                    if concept in concept_strengths:
                        concept_strengths[concept] = max(
                            concept_strengths[concept], 
                            strength
                        )
                    else:
                        concept_strengths[concept] = strength
            
            # Get papers from graph
            papers = graph_service.get_researcher_papers(researcher_id)
            
            # Build personalized graph structure
            nodes = []
            edges = []
            
            # Add concept nodes with memory-based weights
            for concept, strength in concept_strengths.items():
                nodes.append({
                    "id": concept,
                    "type": "concept",
                    "memory_strength": strength,
                    "mastery_level": self._strength_to_mastery(strength),
                    "size": strength * 100  # Visual size based on strength
                })
            
            # Add paper nodes
            for paper in papers:
                nodes.append({
                    "id": paper.get("paper_id"),
                    "type": "paper",
                    "title": paper.get("title"),
                    "read": True
                })
            
            # Find connections in graph
            for i, concept1 in enumerate(list(concept_strengths.keys())):
                for concept2 in list(concept_strengths.keys())[i+1:]:
                    # Check if concepts are connected in graph
                    bridges = graph_service.find_bridge_concepts(concept1, concept2)
                    if bridges:
                        edges.append({
                            "source": concept1,
                            "target": concept2,
                            "weight": (concept_strengths[concept1] + concept_strengths[concept2]) / 2,
                            "bridge_concepts": bridges[:3]
                        })
            
            return {
                "researcher_id": researcher_id,
                "nodes": nodes,
                "edges": edges,
                "graph_statistics": {
                    "total_concepts": len(concept_strengths),
                    "strong_concepts": len([s for s in concept_strengths.values() if s > 0.7]),
                    "weak_concepts": len([s for s in concept_strengths.values() if s < 0.3]),
                    "papers_read": len(papers)
                }
            }
        except Exception as e:
            logger.error(f"Error creating personalized graph view: {e}")
            return {"error": str(e)}
    
    def _strength_to_mastery(self, strength: float) -> str:
        """Convert memory strength to mastery level."""
        if strength > 0.8:
            return "expert"
        elif strength > 0.6:
            return "proficient"
        elif strength > 0.4:
            return "familiar"
        else:
            return "novice"
    
    def serendipitous_discovery(
        self, 
        researcher_id: str
    ) -> List[Dict]:
        """
        Find serendipitous connections between what you know and what you don't.
        
        Discovers:
        - Unexpected but valuable connections
        - Papers at intersection of distant concepts
        - Cross-domain opportunities
        """
        try:
            logger.info(f"Finding serendipitous discoveries for {researcher_id}")
            
            discoveries = []
            
            # Get researcher's strong concepts
            memories = memory_service.recall_paper_memories(
                researcher_id=researcher_id,
                limit=30
            )
            
            known_concepts = set()
            for memory in memories:
                concepts = memory.get("content", {}).get("key_concepts", [])
                known_concepts.update(concepts)
            
            # Find distant but connected concepts
            for concept in list(known_concepts)[:5]:
                # Get concepts 2-3 hops away in graph
                distant_concepts = self._find_distant_concepts(concept, hops=3)
                
                for distant_concept, path in distant_concepts[:3]:
                    if distant_concept not in known_concepts:
                        # This is a serendipitous connection
                        discoveries.append({
                            "type": "distant_connection",
                            "known_concept": concept,
                            "discovered_concept": distant_concept,
                            "path": path,
                            "serendipity_score": 0.8,
                            "insight": f"Unexpected connection between {concept} and {distant_concept}",
                            "action": f"Explore papers on {distant_concept}"
                        })
            
            # Find cross-domain opportunities
            domains = ["machine learning", "neuroscience", "physics", "biology"]
            for domain in domains:
                # Check if researcher has papers in this domain
                domain_papers = graph_service.get_related_papers(domain, limit=5)
                has_domain = any(
                    p.get("paper_id") in [m.get("content", {}).get("paper_id") for m in memories]
                    for p in domain_papers
                )
                
                if not has_domain and known_concepts:
                    # Find connections to this domain
                    sample_concept = list(known_concepts)[0]
                    analogies = graph_reasoning_service.find_analogies(
                        sample_concept, domain, max_analogies=1
                    )
                    
                    if analogies:
                        discoveries.append({
                            "type": "cross_domain",
                            "your_domain": sample_concept,
                            "new_domain": domain,
                            "analogy": analogies[0],
                            "serendipity_score": 0.9,
                            "insight": f"Your knowledge of {sample_concept} could apply to {domain}",
                            "action": f"Explore {domain} literature"
                        })
            
            return discoveries
        except Exception as e:
            logger.error(f"Error finding serendipitous discoveries: {e}")
            return []
    
    def _find_distant_concepts(
        self, 
        concept: str,
        hops: int = 3
    ) -> List[Tuple[str, List[str]]]:
        """Find concepts at specific distance in graph."""
        try:
            with graph_service.driver.session(database=graph_service.database) as session:
                query = """
                MATCH path = (c1:Concept {name: $concept})-[*%d..%d]-(c2:Concept)
                WHERE c1 <> c2
                RETURN c2.name as distant_concept,
                       [node in nodes(path) | node.name] as path_nodes
                LIMIT 10
                """ % (hops, hops)
                
                result = session.run(query, concept=concept)
                
                distant = []
                for record in result:
                    distant.append((
                        record["distant_concept"],
                        record["path_nodes"]
                    ))
                
                return distant
        except Exception as e:
            logger.error(f"Error finding distant concepts: {e}")
            return []
    
    def research_intuition(
        self, 
        researcher_id: str,
        current_context: str
    ) -> Dict:
        """
        Generate research intuition based on memory patterns and graph structure.
        
        Provides:
        - Gut feeling about research directions
        - Pattern-based suggestions
        - Warnings about potential pitfalls
        """
        try:
            logger.info(f"Generating research intuition for {researcher_id}")
            
            # Analyze memory patterns
            memories = memory_service.recall_paper_memories(
                researcher_id=researcher_id,
                limit=50
            )
            
            # Extract patterns
            concept_frequency = {}
            for memory in memories:
                concepts = memory.get("content", {}).get("key_concepts", [])
                for concept in concepts:
                    concept_frequency[concept] = concept_frequency.get(concept, 0) + 1
            
            # Find researcher's "intuitive" areas (high frequency)
            intuitive_concepts = [
                c for c, freq in concept_frequency.items() 
                if freq >= 3
            ]
            
            # Check if current context aligns with intuition
            context_concepts = current_context.lower().split()
            alignment = any(
                concept.lower() in current_context.lower()
                for concept in intuitive_concepts
            )
            
            # Generate intuition
            if alignment:
                intuition = {
                    "confidence": "high",
                    "feeling": "This aligns well with your expertise",
                    "reasoning": f"You have strong memory patterns in: {', '.join(intuitive_concepts[:3])}",
                    "suggestion": "Trust your instincts and dive deeper"
                }
            else:
                intuition = {
                    "confidence": "exploratory",
                    "feeling": "This is outside your comfort zone",
                    "reasoning": "Few memory patterns in this area",
                    "suggestion": "Approach with curiosity, build foundational knowledge first"
                }
            
            # Add graph-based insights
            gaps = memory_consolidation_service.identify_memory_gaps(researcher_id)
            if gaps:
                intuition["warning"] = f"Knowledge gap detected in: {gaps[0].get('concept')}"
            
            return intuition
        except Exception as e:
            logger.error(f"Error generating research intuition: {e}")
            return {"error": str(e)}
    
    def cognitive_load_optimizer(
        self, 
        researcher_id: str
    ) -> Dict:
        """
        Optimize learning based on cognitive load and memory capacity.
        
        Recommends:
        - How many papers to read
        - When to review
        - What to focus on
        - When to take breaks
        """
        try:
            logger.info(f"Optimizing cognitive load for {researcher_id}")
            
            # Get recent reading activity
            recent_memories = memory_service.get_recent_context(
                researcher_id=researcher_id,
                hours=24
            )
            
            # Calculate cognitive load
            papers_today = len([
                m for m in recent_memories
                if m.get("content", {}).get("type") == "paper_reading"
            ])
            
            # Memory strength analysis
            all_memories = memory_service.recall_paper_memories(
                researcher_id=researcher_id,
                limit=50
            )
            
            current_time = datetime.now()
            weak_memories = [
                m for m in all_memories
                if memory_consolidation_service.calculate_memory_strength(m, current_time) < 0.4
            ]
            
            # Generate recommendations
            recommendations = []
            
            if papers_today > 5:
                recommendations.append({
                    "type": "overload_warning",
                    "message": "You've read many papers today. Consider taking a break.",
                    "reason": "Cognitive overload reduces retention"
                })
            elif papers_today == 0:
                recommendations.append({
                    "type": "engagement",
                    "message": "Good time to read a new paper",
                    "reason": "Fresh cognitive capacity available"
                })
            
            if len(weak_memories) > 10:
                recommendations.append({
                    "type": "review_needed",
                    "message": f"Review {len(weak_memories)} papers with weak memory",
                    "reason": "Strengthen memories before they fade",
                    "papers_to_review": [
                        m.get("content", {}).get("title")
                        for m in weak_memories[:5]
                    ]
                })
            
            # Optimal reading schedule
            optimal_schedule = {
                "papers_per_day": 3,
                "review_frequency": "every 3 days",
                "deep_reading_time": "morning",
                "review_time": "evening"
            }
            
            return {
                "current_load": {
                    "papers_today": papers_today,
                    "load_level": "high" if papers_today > 5 else "optimal" if papers_today <= 3 else "moderate"
                },
                "memory_health": {
                    "total_memories": len(all_memories),
                    "weak_memories": len(weak_memories),
                    "needs_review": len(weak_memories) > 10
                },
                "recommendations": recommendations,
                "optimal_schedule": optimal_schedule
            }
        except Exception as e:
            logger.error(f"Error optimizing cognitive load: {e}")
            return {"error": str(e)}
    
    def learning_path_generator(
        self, 
        researcher_id: str,
        target_concept: str
    ) -> Dict:
        """
        Generate personalized learning path using memory and graph.
        
        Creates path from current knowledge to target concept:
        1. Assess current knowledge (memory)
        2. Find path in graph
        3. Order by difficulty and prerequisites
        4. Consider memory capacity
        """
        try:
            logger.info(f"Generating learning path to: {target_concept}")
            
            # Get current knowledge
            memories = memory_service.recall_paper_memories(
                researcher_id=researcher_id,
                limit=30
            )
            
            known_concepts = set()
            for memory in memories:
                concepts = memory.get("content", {}).get("key_concepts", [])
                known_concepts.update(concepts)
            
            # Find closest known concept to target
            closest_concept = None
            min_distance = float('inf')
            
            for concept in list(known_concepts)[:10]:
                paths = graph_service.find_connections(
                    source_concept=concept,
                    target_concept=target_concept,
                    max_hops=5
                )
                if paths and paths[0]["path_length"] < min_distance:
                    min_distance = paths[0]["path_length"]
                    closest_concept = concept
            
            if not closest_concept:
                return {
                    "error": "No learning path found",
                    "suggestion": "Start with foundational papers in this area"
                }
            
            # Get the path
            paths = graph_service.find_connections(
                source_concept=closest_concept,
                target_concept=target_concept,
                max_hops=5
            )
            
            if not paths:
                return {"error": "No path found"}
            
            path = paths[0]
            
            # Create learning steps
            learning_steps = []
            for i, concept in enumerate(path["nodes"]):
                if concept not in known_concepts:
                    learning_steps.append({
                        "step": i + 1,
                        "concept": concept,
                        "difficulty": "easy" if i < 2 else "medium" if i < 4 else "hard",
                        "estimated_time": f"{(i+1) * 2} hours",
                        "action": f"Read 2-3 papers on {concept}"
                    })
            
            return {
                "target_concept": target_concept,
                "starting_point": closest_concept,
                "total_steps": len(learning_steps),
                "estimated_duration": f"{len(learning_steps) * 2} hours",
                "learning_path": learning_steps,
                "difficulty_level": "progressive",
                "success_probability": 0.8 if len(learning_steps) < 5 else 0.6
            }
        except Exception as e:
            logger.error(f"Error generating learning path: {e}")
            return {"error": str(e)}


# Global instance
memory_graph_fusion_service = MemoryGraphFusionService()
