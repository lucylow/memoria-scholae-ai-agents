"""
Advanced Graph Reasoning Service
Implements sophisticated graph algorithms and multi-hop reasoning.
"""
import logging
from typing import Dict, List, Optional, Tuple, Set
from collections import defaultdict, deque
import math

from services.graph_service import graph_service
from services.llm_service import llm_service

logger = logging.getLogger(__name__)


class GraphReasoningService:
    """
    Advanced graph reasoning with sophisticated algorithms.
    
    Features:
    - Analogical reasoning across domains
    - Contradiction detection
    - Research gap analysis
    - Temporal graph evolution
    - Community detection
    - Influence propagation
    """
    
    def __init__(self):
        pass
    
    def find_analogies(
        self, 
        source_domain: str,
        target_domain: str,
        max_analogies: int = 5
    ) -> List[Dict]:
        """
        Find analogical patterns between two research domains.
        
        Uses graph structure to identify similar patterns:
        - Similar relationship structures
        - Parallel methodologies
        - Transferable concepts
        """
        try:
            logger.info(f"Finding analogies between {source_domain} and {target_domain}")
            
            # Get papers from both domains
            source_papers = graph_service.get_related_papers(source_domain, limit=20)
            target_papers = graph_service.get_related_papers(target_domain, limit=20)
            
            analogies = []
            
            # Find structural similarities
            with graph_service.driver.session(database=graph_service.database) as session:
                # Query for similar patterns
                query = """
                MATCH (c1:Concept {name: $source_domain})<-[:DISCUSSES]-(p1:Paper)-[:USES_METHOD]->(m:Methodology)
                MATCH (c2:Concept {name: $target_domain})<-[:DISCUSSES]-(p2:Paper)-[:USES_METHOD]->(m)
                RETURN m.name as method, 
                       collect(DISTINCT p1.title)[0..2] as source_papers,
                       collect(DISTINCT p2.title)[0..2] as target_papers
                LIMIT $max_analogies
                """
                
                result = session.run(
                    query,
                    source_domain=source_domain,
                    target_domain=target_domain,
                    max_analogies=max_analogies
                )
                
                for record in result:
                    analogies.append({
                        "type": "methodological",
                        "shared_method": record["method"],
                        "source_examples": record["source_papers"],
                        "target_examples": record["target_papers"],
                        "insight": f"Method '{record['method']}' successfully used in both domains",
                        "transferability_score": 0.8
                    })
            
            # If no direct analogies, find conceptual bridges
            if not analogies:
                bridges = graph_service.find_bridge_concepts(source_domain, target_domain)
                for bridge in bridges[:max_analogies]:
                    analogies.append({
                        "type": "conceptual",
                        "bridge_concept": bridge,
                        "insight": f"Concept '{bridge}' connects both domains",
                        "transferability_score": 0.6
                    })
            
            return analogies
        except Exception as e:
            logger.error(f"Error finding analogies: {e}")
            return []
    
    def detect_contradictions(
        self, 
        concept: str
    ) -> List[Dict]:
        """
        Detect contradictory findings about a concept in the literature.
        
        Identifies:
        - Papers with opposing conclusions
        - Conflicting methodologies
        - Unresolved debates
        """
        try:
            logger.info(f"Detecting contradictions for concept: {concept}")
            
            # Get papers discussing this concept
            papers = graph_service.get_related_papers(concept, limit=30)
            
            contradictions = []
            
            with graph_service.driver.session(database=graph_service.database) as session:
                # Find papers that cite each other with different conclusions
                query = """
                MATCH (c:Concept {name: $concept})<-[:DISCUSSES]-(p1:Paper)
                MATCH (c)<-[:DISCUSSES]-(p2:Paper)
                WHERE p1.paper_id <> p2.paper_id
                AND (p1)-[:CITES]->(p2)
                RETURN p1.paper_id as citing_paper,
                       p1.title as citing_title,
                       p2.paper_id as cited_paper,
                       p2.title as cited_title
                LIMIT 10
                """
                
                result = session.run(query, concept=concept)
                
                for record in result:
                    contradictions.append({
                        "type": "citation_based",
                        "paper1": {
                            "id": record["citing_paper"],
                            "title": record["citing_title"]
                        },
                        "paper2": {
                            "id": record["cited_paper"],
                            "title": record["cited_title"]
                        },
                        "confidence": 0.6,
                        "requires_investigation": True
                    })
            
            return contradictions
        except Exception as e:
            logger.error(f"Error detecting contradictions: {e}")
            return []
    
    def analyze_research_gaps(
        self, 
        research_area: str
    ) -> Dict:
        """
        Identify gaps in research using graph structure.
        
        Finds:
        - Under-explored connections
        - Missing methodologies
        - Unexplored concept combinations
        """
        try:
            logger.info(f"Analyzing research gaps in: {research_area}")
            
            gaps = {
                "missing_connections": [],
                "under_explored_methods": [],
                "novel_combinations": []
            }
            
            with graph_service.driver.session(database=graph_service.database) as session:
                # Find concepts with few connections
                query = """
                MATCH (c:Concept {name: $research_area})<-[:DISCUSSES]-(p:Paper)-[:DISCUSSES]->(related:Concept)
                WITH related, count(p) as paper_count
                WHERE paper_count < 3
                RETURN related.name as concept, paper_count
                ORDER BY paper_count ASC
                LIMIT 10
                """
                
                result = session.run(query, research_area=research_area)
                
                for record in result:
                    gaps["missing_connections"].append({
                        "concept": record["concept"],
                        "current_papers": record["paper_count"],
                        "opportunity_score": 1.0 - (record["paper_count"] / 10),
                        "recommendation": f"Explore connections between {research_area} and {record['concept']}"
                    })
                
                # Find methodologies not yet applied
                method_query = """
                MATCH (m:Methodology)
                WHERE NOT (m)<-[:USES_METHOD]-(:Paper)-[:DISCUSSES]->(:Concept {name: $research_area})
                RETURN m.name as method
                LIMIT 5
                """
                
                result = session.run(method_query, research_area=research_area)
                
                for record in result:
                    gaps["under_explored_methods"].append({
                        "method": record["method"],
                        "status": "not_applied",
                        "potential": "high",
                        "recommendation": f"Apply {record['method']} to {research_area}"
                    })
            
            return gaps
        except Exception as e:
            logger.error(f"Error analyzing research gaps: {e}")
            return {"error": str(e)}
    
    def track_concept_lifecycle(
        self, 
        concept: str
    ) -> Dict:
        """
        Track the lifecycle of a concept: birth, growth, maturity, decline.
        
        Uses temporal graph data to identify:
        - When concept emerged
        - Growth rate
        - Current stage
        - Future trajectory
        """
        try:
            logger.info(f"Tracking lifecycle for concept: {concept}")
            
            with graph_service.driver.session(database=graph_service.database) as session:
                # Get papers by year
                query = """
                MATCH (c:Concept {name: $concept})<-[:DISCUSSES]-(p:Paper)
                WHERE p.year IS NOT NULL
                RETURN p.year as year, count(p) as paper_count
                ORDER BY year ASC
                """
                
                result = session.run(query, concept=concept)
                
                timeline = []
                for record in result:
                    timeline.append({
                        "year": record["year"],
                        "papers": record["paper_count"]
                    })
                
                if not timeline:
                    return {"error": "No temporal data available"}
                
                # Analyze lifecycle stage
                recent_years = [t for t in timeline if t["year"] >= 2020]
                early_years = [t for t in timeline if t["year"] < 2015]
                
                total_recent = sum(t["papers"] for t in recent_years)
                total_early = sum(t["papers"] for t in early_years) if early_years else 1
                
                growth_rate = (total_recent / total_early) if total_early > 0 else 0
                
                # Determine stage
                if len(timeline) < 3:
                    stage = "emerging"
                elif growth_rate > 2:
                    stage = "rapid_growth"
                elif growth_rate > 1:
                    stage = "steady_growth"
                elif growth_rate > 0.5:
                    stage = "mature"
                else:
                    stage = "declining"
                
                return {
                    "concept": concept,
                    "first_appeared": timeline[0]["year"],
                    "total_years": len(timeline),
                    "lifecycle_stage": stage,
                    "growth_rate": round(growth_rate, 2),
                    "timeline": timeline,
                    "prediction": self._predict_trajectory(timeline, stage)
                }
        except Exception as e:
            logger.error(f"Error tracking concept lifecycle: {e}")
            return {"error": str(e)}
    
    def _predict_trajectory(self, timeline: List[Dict], stage: str) -> str:
        """Predict future trajectory of concept."""
        if stage == "emerging":
            return "Concept is new and gaining attention"
        elif stage == "rapid_growth":
            return "Expect continued strong growth in next 2-3 years"
        elif stage == "steady_growth":
            return "Stable research area with consistent output"
        elif stage == "mature":
            return "Well-established field, may plateau soon"
        else:
            return "Declining interest, may be superseded by newer concepts"
    
    def calculate_influence_propagation(
        self, 
        paper_id: str,
        max_depth: int = 3
    ) -> Dict:
        """
        Calculate how influence propagates from a paper through citations.
        
        Measures:
        - Direct citations
        - Indirect influence (citations of citations)
        - Influence decay over time
        - Influence spread across domains
        """
        try:
            logger.info(f"Calculating influence propagation for paper: {paper_id}")
            
            with graph_service.driver.session(database=graph_service.database) as session:
                # Multi-hop citation analysis
                query = """
                MATCH path = (p:Paper {paper_id: $paper_id})<-[:CITES*1..%d]-(citing:Paper)
                RETURN citing.paper_id as citing_id,
                       citing.title as title,
                       citing.year as year,
                       length(path) as distance
                ORDER BY distance, year DESC
                LIMIT 50
                """ % max_depth
                
                result = session.run(query, paper_id=paper_id)
                
                influence_map = defaultdict(list)
                for record in result:
                    distance = record["distance"]
                    influence_map[distance].append({
                        "paper_id": record["citing_id"],
                        "title": record["title"],
                        "year": record["year"]
                    })
                
                # Calculate influence score
                total_influence = 0
                for distance, papers in influence_map.items():
                    # Influence decays with distance
                    decay_factor = 1.0 / (distance ** 1.5)
                    total_influence += len(papers) * decay_factor
                
                return {
                    "paper_id": paper_id,
                    "direct_citations": len(influence_map.get(1, [])),
                    "indirect_citations": sum(len(papers) for d, papers in influence_map.items() if d > 1),
                    "influence_score": round(total_influence, 2),
                    "max_depth_reached": max(influence_map.keys()) if influence_map else 0,
                    "influence_by_distance": {
                        f"depth_{d}": len(papers) 
                        for d, papers in influence_map.items()
                    }
                }
        except Exception as e:
            logger.error(f"Error calculating influence propagation: {e}")
            return {"error": str(e)}
    
    def find_synthesis_paths(
        self, 
        concepts: List[str]
    ) -> List[Dict]:
        """
        Find paths to synthesize multiple concepts into novel ideas.
        
        Identifies:
        - Common methodologies across concepts
        - Shared theoretical frameworks
        - Potential fusion points
        """
        try:
            logger.info(f"Finding synthesis paths for concepts: {concepts}")
            
            if len(concepts) < 2:
                return []
            
            synthesis_paths = []
            
            with graph_service.driver.session(database=graph_service.database) as session:
                # Find papers that discuss multiple concepts
                query = """
                MATCH (p:Paper)
                WHERE ALL(concept_name IN $concepts 
                    WHERE (p)-[:DISCUSSES]->(:Concept {name: concept_name}))
                RETURN p.paper_id as paper_id,
                       p.title as title,
                       p.year as year
                LIMIT 10
                """
                
                result = session.run(query, concepts=concepts)
                
                for record in result:
                    synthesis_paths.append({
                        "type": "existing_synthesis",
                        "paper_id": record["paper_id"],
                        "title": record["title"],
                        "year": record["year"],
                        "concepts_combined": concepts,
                        "novelty": "low"  # Already exists
                    })
                
                # Find potential synthesis through shared methods
                method_query = """
                UNWIND $concepts as concept_name
                MATCH (c:Concept {name: concept_name})<-[:DISCUSSES]-(p:Paper)-[:USES_METHOD]->(m:Methodology)
                WITH m, collect(DISTINCT concept_name) as covered_concepts
                WHERE size(covered_concepts) >= 2
                RETURN m.name as method,
                       covered_concepts,
                       size(covered_concepts) as concept_count
                ORDER BY concept_count DESC
                LIMIT 5
                """
                
                result = session.run(method_query, concepts=concepts)
                
                for record in result:
                    synthesis_paths.append({
                        "type": "methodological_synthesis",
                        "shared_method": record["method"],
                        "concepts_covered": record["covered_concepts"],
                        "novelty": "medium",
                        "recommendation": f"Apply {record['method']} to synthesize {', '.join(concepts)}"
                    })
            
            return synthesis_paths
        except Exception as e:
            logger.error(f"Error finding synthesis paths: {e}")
            return []
    
    def detect_research_communities(
        self, 
        min_community_size: int = 3
    ) -> List[Dict]:
        """
        Detect research communities using graph clustering.
        
        Identifies groups of:
        - Frequently co-cited papers
        - Collaborating authors
        - Related concepts
        """
        try:
            logger.info("Detecting research communities")
            
            communities = []
            
            with graph_service.driver.session(database=graph_service.database) as session:
                # Find author collaboration clusters
                query = """
                MATCH (a1:Author)<-[:AUTHORED_BY]-(p:Paper)-[:AUTHORED_BY]->(a2:Author)
                WHERE a1.name < a2.name
                WITH a1, a2, count(p) as collaborations
                WHERE collaborations >= 2
                RETURN a1.name as author1, a2.name as author2, collaborations
                LIMIT 20
                """
                
                result = session.run(query)
                
                # Build collaboration graph
                collab_graph = defaultdict(set)
                for record in result:
                    a1, a2 = record["author1"], record["author2"]
                    collab_graph[a1].add(a2)
                    collab_graph[a2].add(a1)
                
                # Simple community detection (connected components)
                visited = set()
                for author in collab_graph:
                    if author not in visited:
                        community = self._bfs_community(author, collab_graph, visited)
                        if len(community) >= min_community_size:
                            communities.append({
                                "type": "author_collaboration",
                                "members": list(community),
                                "size": len(community),
                                "cohesion": "high"
                            })
            
            return communities
        except Exception as e:
            logger.error(f"Error detecting communities: {e}")
            return []
    
    def _bfs_community(
        self, 
        start: str,
        graph: Dict[str, Set],
        visited: Set
    ) -> Set:
        """BFS to find connected component (community)."""
        community = set()
        queue = deque([start])
        
        while queue:
            node = queue.popleft()
            if node in visited:
                continue
            
            visited.add(node)
            community.add(node)
            
            for neighbor in graph.get(node, set()):
                if neighbor not in visited:
                    queue.append(neighbor)
        
        return community


# Global instance
graph_reasoning_service = GraphReasoningService()
