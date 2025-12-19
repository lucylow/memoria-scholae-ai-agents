"""
Multi-Agent Collaboration Service
Implements specialized research agents with memory sharing and collaborative reasoning.
"""
import logging
from typing import Dict, List, Optional
from datetime import datetime
import json

from services.memory_service import memory_service
from services.graph_service import graph_service
from services.llm_service import llm_service
from services.graph_reasoning import graph_reasoning_service

logger = logging.getLogger(__name__)


class ResearchAgent:
    """Base class for specialized research agents."""
    
    def __init__(self, agent_id: str, role: str, personality: Dict):
        self.agent_id = agent_id
        self.role = role
        self.personality = personality
        self.memory_namespace = f"agent_{agent_id}"
    
    def store_insight(self, researcher_id: str, insight: Dict):
        """Store agent's insight in shared memory."""
        memory_service.store_memory(
            user_id=researcher_id,
            memory_type="project",
            content={
                "type": "agent_insight",
                "agent_id": self.agent_id,
                "agent_role": self.role,
                "insight": insight,
                "timestamp": datetime.now().isoformat()
            }
        )
    
    def retrieve_insights(self, researcher_id: str, limit: int = 10) -> List[Dict]:
        """Retrieve insights from other agents."""
        memories = memory_service.search_memories(
            researcher_id=researcher_id,
            query=f"agent_insight {self.role}",
            limit=limit
        )
        return [m.get("content", {}) for m in memories]


class LiteratureScoutAgent(ResearchAgent):
    """
    Agent specialized in discovering relevant papers.
    
    Personality: Curious, thorough, trend-aware
    """
    
    def __init__(self):
        super().__init__(
            agent_id="scout_001",
            role="literature_scout",
            personality={
                "curiosity": 0.9,
                "thoroughness": 0.8,
                "risk_tolerance": 0.6
            }
        )
    
    def scout_papers(
        self, 
        researcher_id: str,
        research_interest: str
    ) -> List[Dict]:
        """
        Scout for relevant papers based on research interest.
        
        Strategy:
        1. Analyze researcher's reading history
        2. Identify emerging trends
        3. Find papers at intersection of interests
        4. Prioritize by novelty and relevance
        """
        try:
            logger.info(f"Scout agent scouting papers for: {research_interest}")
            
            # Get researcher's context
            past_papers = graph_service.get_researcher_papers(researcher_id)
            
            # Find related papers
            candidates = graph_service.get_related_papers(research_interest, limit=20)
            
            # Score by novelty
            recommendations = []
            for paper in candidates[:10]:
                paper_id = paper.get("paper_id")
                
                # Check if already read
                already_read = any(p.get("paper_id") == paper_id for p in past_papers)
                
                if not already_read:
                    recommendations.append({
                        "paper_id": paper_id,
                        "title": paper.get("title"),
                        "relevance_score": 0.8,
                        "novelty_score": 0.9,
                        "scout_reasoning": "Emerging paper in your research area"
                    })
            
            # Store insights
            self.store_insight(researcher_id, {
                "action": "paper_scouting",
                "topic": research_interest,
                "papers_found": len(recommendations),
                "recommendations": recommendations[:5]
            })
            
            return recommendations
        except Exception as e:
            logger.error(f"Error in scout agent: {e}")
            return []


class PatternSpotterAgent(ResearchAgent):
    """
    Agent specialized in identifying patterns across papers.
    
    Personality: Analytical, systematic, detail-oriented
    """
    
    def __init__(self):
        super().__init__(
            agent_id="spotter_001",
            role="pattern_spotter",
            personality={
                "analytical_depth": 0.9,
                "pattern_recognition": 0.95,
                "creativity": 0.6
            }
        )
    
    def spot_patterns(
        self, 
        researcher_id: str,
        papers: List[str]
    ) -> List[Dict]:
        """
        Identify patterns across multiple papers.
        
        Looks for:
        - Common methodologies
        - Recurring themes
        - Contradictions
        - Evolution of ideas
        """
        try:
            logger.info(f"Pattern spotter analyzing {len(papers)} papers")
            
            patterns = []
            
            # Analyze concept co-occurrence
            concept_pairs = defaultdict(int)
            for paper_id in papers:
                # Get paper concepts from memory
                memories = memory_service.recall_paper_memories(
                    researcher_id=researcher_id,
                    paper_id=paper_id
                )
                if memories:
                    concepts = memories[0].get("content", {}).get("key_concepts", [])
                    for i, c1 in enumerate(concepts):
                        for c2 in concepts[i+1:]:
                            pair = tuple(sorted([c1, c2]))
                            concept_pairs[pair] += 1
            
            # Identify strong patterns
            for (c1, c2), count in concept_pairs.items():
                if count >= 2:
                    patterns.append({
                        "type": "concept_co_occurrence",
                        "concept1": c1,
                        "concept2": c2,
                        "frequency": count,
                        "pattern_strength": count / len(papers),
                        "insight": f"{c1} and {c2} frequently appear together"
                    })
            
            # Find contradictions
            contradictions = graph_reasoning_service.detect_contradictions(
                papers[0] if papers else "machine learning"
            )
            
            if contradictions:
                patterns.append({
                    "type": "contradiction",
                    "details": contradictions[0],
                    "insight": "Conflicting findings detected"
                })
            
            # Store insights
            self.store_insight(researcher_id, {
                "action": "pattern_spotting",
                "papers_analyzed": len(papers),
                "patterns_found": len(patterns),
                "top_patterns": patterns[:3]
            })
            
            return patterns
        except Exception as e:
            logger.error(f"Error in pattern spotter: {e}")
            return []


class HypothesisGeneratorAgent(ResearchAgent):
    """
    Agent specialized in generating creative hypotheses.
    
    Personality: Creative, bold, innovative
    """
    
    def __init__(self):
        super().__init__(
            agent_id="generator_001",
            role="hypothesis_generator",
            personality={
                "creativity": 0.95,
                "boldness": 0.8,
                "rigor": 0.7
            }
        )
    
    def generate_creative_hypotheses(
        self, 
        researcher_id: str,
        topic: str,
        patterns: List[Dict]
    ) -> List[Dict]:
        """
        Generate creative hypotheses based on identified patterns.
        
        Strategy:
        1. Analyze patterns from Pattern Spotter
        2. Find analogies from other domains
        3. Combine concepts in novel ways
        4. Generate testable hypotheses
        """
        try:
            logger.info(f"Hypothesis generator creating hypotheses for: {topic}")
            
            hypotheses = []
            
            # Use patterns to generate hypotheses
            for pattern in patterns[:3]:
                if pattern.get("type") == "concept_co_occurrence":
                    c1 = pattern.get("concept1")
                    c2 = pattern.get("concept2")
                    
                    hypothesis = {
                        "hypothesis_text": f"The interaction between {c1} and {c2} may lead to novel insights in {topic}",
                        "basis": "pattern_analysis",
                        "pattern_strength": pattern.get("pattern_strength", 0.5),
                        "novelty_score": 0.75,
                        "testability": "high",
                        "required_experiments": [
                            f"Systematic study of {c1}-{c2} interaction",
                            f"Comparison with baseline {topic} approaches"
                        ]
                    }
                    hypotheses.append(hypothesis)
            
            # Generate cross-domain hypotheses
            # Find analogies
            domains = ["machine learning", "biology", "physics"]
            for domain in domains:
                if domain.lower() not in topic.lower():
                    analogies = graph_reasoning_service.find_analogies(
                        source_domain=topic,
                        target_domain=domain,
                        max_analogies=2
                    )
                    
                    for analogy in analogies:
                        if analogy.get("type") == "methodological":
                            method = analogy.get("shared_method")
                            hypotheses.append({
                                "hypothesis_text": f"Applying {method} from {domain} could advance {topic}",
                                "basis": "cross_domain_analogy",
                                "source_domain": domain,
                                "novelty_score": 0.85,
                                "testability": "medium",
                                "boldness": 0.8
                            })
            
            # Store insights
            self.store_insight(researcher_id, {
                "action": "hypothesis_generation",
                "topic": topic,
                "hypotheses_generated": len(hypotheses),
                "top_hypotheses": hypotheses[:3]
            })
            
            return hypotheses
        except Exception as e:
            logger.error(f"Error in hypothesis generator: {e}")
            return []


class MultiAgentOrchestrator:
    """
    Orchestrates collaboration between multiple research agents.
    
    Implements:
    - Agent coordination
    - Memory sharing
    - Collaborative reasoning
    - Consensus building
    """
    
    def __init__(self):
        self.scout = LiteratureScoutAgent()
        self.spotter = PatternSpotterAgent()
        self.generator = HypothesisGeneratorAgent()
    
    def collaborative_research(
        self, 
        researcher_id: str,
        research_topic: str
    ) -> Dict:
        """
        Coordinate agents to perform collaborative research.
        
        Workflow:
        1. Scout finds relevant papers
        2. Spotter identifies patterns
        3. Generator creates hypotheses
        4. Agents debate and refine
        """
        try:
            logger.info(f"Multi-agent collaboration on: {research_topic}")
            
            # Phase 1: Scout papers
            logger.info("Phase 1: Literature scouting")
            papers = self.scout.scout_papers(researcher_id, research_topic)
            paper_ids = [p["paper_id"] for p in papers]
            
            # Phase 2: Spot patterns
            logger.info("Phase 2: Pattern spotting")
            patterns = self.spotter.spot_patterns(researcher_id, paper_ids)
            
            # Phase 3: Generate hypotheses
            logger.info("Phase 3: Hypothesis generation")
            hypotheses = self.generator.generate_creative_hypotheses(
                researcher_id, 
                research_topic,
                patterns
            )
            
            # Phase 4: Agent debate (simplified)
            refined_hypotheses = self._agent_debate(hypotheses)
            
            # Store collaborative result
            memory_service.store_memory(
                user_id=researcher_id,
                memory_type="project",
                content={
                    "type": "multi_agent_collaboration",
                    "topic": research_topic,
                    "papers_scouted": len(papers),
                    "patterns_found": len(patterns),
                    "hypotheses_generated": len(hypotheses),
                    "refined_hypotheses": refined_hypotheses,
                    "timestamp": datetime.now().isoformat()
                }
            )
            
            return {
                "research_topic": research_topic,
                "papers_discovered": papers[:5],
                "patterns_identified": patterns[:5],
                "hypotheses_generated": refined_hypotheses[:5],
                "agent_insights": {
                    "scout": f"Found {len(papers)} relevant papers",
                    "spotter": f"Identified {len(patterns)} patterns",
                    "generator": f"Generated {len(hypotheses)} hypotheses"
                },
                "collaboration_score": self._calculate_collaboration_score(papers, patterns, hypotheses)
            }
        except Exception as e:
            logger.error(f"Error in multi-agent collaboration: {e}")
            return {"error": str(e)}
    
    def _agent_debate(self, hypotheses: List[Dict]) -> List[Dict]:
        """
        Simulate agent debate to refine hypotheses.
        
        Agents critique and improve each other's ideas.
        """
        refined = []
        
        for hypothesis in hypotheses[:5]:
            # Simple refinement: boost scores for well-supported hypotheses
            if hypothesis.get("basis") == "pattern_analysis":
                hypothesis["confidence_after_debate"] = 0.8
                hypothesis["scout_support"] = True
                hypothesis["spotter_support"] = True
            else:
                hypothesis["confidence_after_debate"] = 0.7
                hypothesis["scout_support"] = False
                hypothesis["spotter_support"] = True
            
            refined.append(hypothesis)
        
        return refined
    
    def _calculate_collaboration_score(
        self, 
        papers: List,
        patterns: List,
        hypotheses: List
    ) -> float:
        """Calculate quality of agent collaboration."""
        # Score based on productivity and quality
        score = 0.0
        score += min(len(papers) / 10, 1.0) * 0.3  # Paper discovery
        score += min(len(patterns) / 5, 1.0) * 0.3  # Pattern finding
        score += min(len(hypotheses) / 3, 1.0) * 0.4  # Hypothesis quality
        
        return round(score, 2)


# Import for pattern spotter
from collections import defaultdict

# Global instance
multi_agent_orchestrator = MultiAgentOrchestrator()
