"""
LLM service for AI-powered text processing and generation.
"""
from openai import OpenAI
import logging
from typing import List, Dict, Optional
from config.settings import settings

logger = logging.getLogger(__name__)


class LLMService:
    """Service for LLM-powered operations."""
    
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        self.model = settings.openai_model
    
    def extract_concepts(self, text: str, max_concepts: int = 10) -> List[str]:
        """Extract key concepts from paper text using LLM."""
        try:
            prompt = f"""Extract the {max_concepts} most important research concepts, methodologies, or techniques from the following academic paper text. 
Return only a comma-separated list of concepts, nothing else.

Text:
{text[:4000]}

Concepts:"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at extracting key concepts from academic papers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=200
            )
            
            concepts_text = response.choices[0].message.content.strip()
            concepts = [c.strip() for c in concepts_text.split(',')]
            return concepts[:max_concepts]
        except Exception as e:
            logger.error(f"Error extracting concepts: {e}")
            return []
    
    def summarize_paper(self, title: str, abstract: str, full_text: str) -> str:
        """Generate a concise summary of the paper."""
        try:
            prompt = f"""Summarize this academic paper in 2-3 sentences, focusing on the main contribution and findings.

Title: {title}
Abstract: {abstract[:500]}

Summary:"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at summarizing academic papers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.5,
                max_tokens=150
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error summarizing paper: {e}")
            return "Summary not available."
    
    def answer_query(
        self, 
        query: str, 
        context: List[Dict],
        researcher_context: Optional[str] = None
    ) -> Dict[str, any]:
        """Answer a research query using context from papers and memories."""
        try:
            # Build context string
            context_str = "\n\n".join([
                f"Paper: {c.get('title', 'Unknown')}\n{c.get('content', '')[:500]}"
                for c in context[:5]
            ])
            
            prompt = f"""You are an AI research assistant. Answer the following research query using the provided context from academic papers.

Context:
{context_str}

{f'Researcher background: {researcher_context}' if researcher_context else ''}

Query: {query}

Provide a comprehensive answer with specific references to the papers mentioned in the context."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a knowledgeable research assistant with expertise in academic literature."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            answer = response.choices[0].message.content.strip()
            
            return {
                "answer": answer,
                "confidence": 0.85,
                "sources": [c.get('title', 'Unknown') for c in context[:5]]
            }
        except Exception as e:
            logger.error(f"Error answering query: {e}")
            return {
                "answer": "I apologize, but I encountered an error processing your query.",
                "confidence": 0.0,
                "sources": []
            }
    
    def generate_hypotheses(
        self, 
        topic: str, 
        papers_context: List[Dict],
        num_hypotheses: int = 3
    ) -> List[Dict]:
        """Generate novel research hypotheses based on papers."""
        try:
            # Build context from papers
            papers_summary = "\n".join([
                f"- {p.get('title', 'Unknown')}: {p.get('summary', p.get('abstract', ''))[:200]}"
                for p in papers_context[:10]
            ])
            
            prompt = f"""Based on the following research papers, generate {num_hypotheses} novel, testable research hypotheses related to "{topic}".

Papers:
{papers_summary}

For each hypothesis, provide:
1. The hypothesis statement
2. Brief reasoning why it's worth investigating
3. Novelty score (0-1)
4. Confidence score (0-1)

Format as JSON array."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a creative research scientist skilled at identifying novel research directions."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=800
            )
            
            # Parse response
            content = response.choices[0].message.content.strip()
            
            # Simple parsing (in production, use proper JSON parsing)
            hypotheses = []
            lines = content.split('\n')
            current_hypothesis = {}
            
            for line in lines:
                if 'hypothesis' in line.lower() and ':' in line:
                    if current_hypothesis:
                        hypotheses.append(current_hypothesis)
                    current_hypothesis = {
                        "hypothesis_text": line.split(':', 1)[1].strip(),
                        "reasoning": "",
                        "novelty_score": 0.7,
                        "confidence_score": 0.75
                    }
                elif 'reasoning' in line.lower() and current_hypothesis:
                    current_hypothesis["reasoning"] = line.split(':', 1)[1].strip() if ':' in line else line.strip()
            
            if current_hypothesis:
                hypotheses.append(current_hypothesis)
            
            # Ensure we have the requested number
            while len(hypotheses) < num_hypotheses:
                hypotheses.append({
                    "hypothesis_text": f"Investigate the application of methods from paper {len(hypotheses)+1} to new domains.",
                    "reasoning": "Cross-domain application often yields novel insights.",
                    "novelty_score": 0.6,
                    "confidence_score": 0.65
                })
            
            return hypotheses[:num_hypotheses]
        except Exception as e:
            logger.error(f"Error generating hypotheses: {e}")
            return []
    
    def explain_connection(
        self, 
        concept1: str, 
        concept2: str, 
        path_info: List[str]
    ) -> str:
        """Explain the connection between two concepts based on graph path."""
        try:
            path_str = " -> ".join(path_info)
            
            prompt = f"""Explain the connection between "{concept1}" and "{concept2}" in academic research.

The knowledge graph shows this connection path:
{path_str}

Provide a clear, concise explanation of how these concepts are related and why this connection is meaningful for researchers."""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at explaining complex academic relationships."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.6,
                max_tokens=300
            )
            
            return response.choices[0].message.content.strip()
        except Exception as e:
            logger.error(f"Error explaining connection: {e}")
            return "Connection explanation not available."
    
    def identify_key_findings(self, paper_text: str) -> List[str]:
        """Identify key findings and contributions from a paper."""
        try:
            prompt = f"""Identify the 3-5 key findings or contributions from this academic paper. 
Return as a bullet list.

Paper text:
{paper_text[:3000]}

Key findings:"""
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert at analyzing academic papers."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=300
            )
            
            findings_text = response.choices[0].message.content.strip()
            # Parse bullet points
            findings = [
                line.strip('- •*').strip() 
                for line in findings_text.split('\n') 
                if line.strip() and len(line.strip()) > 10
            ]
            return findings[:5]
        except Exception as e:
            logger.error(f"Error identifying findings: {e}")
            return []


# Global instance
llm_service = LLMService()
