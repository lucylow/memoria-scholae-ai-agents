"""
Data models and schemas for MemoriaScholae.
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class MemoryType(str, Enum):
    """Types of memory in the system."""
    WORKING = "working"
    PERSONAL = "personal"
    PROJECT = "project"
    INSTITUTIONAL = "institutional"


class PaperMetadata(BaseModel):
    """Metadata for an academic paper."""
    paper_id: str
    title: str
    authors: List[str]
    abstract: Optional[str] = None
    year: Optional[int] = None
    venue: Optional[str] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    keywords: List[str] = Field(default_factory=list)
    upload_date: datetime = Field(default_factory=datetime.now)


class PaperContent(BaseModel):
    """Full content of a paper."""
    paper_id: str
    full_text: str
    sections: Dict[str, str] = Field(default_factory=dict)
    figures: List[str] = Field(default_factory=list)
    tables: List[str] = Field(default_factory=list)
    references: List[str] = Field(default_factory=list)


class PaperUploadRequest(BaseModel):
    """Request for uploading a paper."""
    researcher_id: str
    notes: Optional[str] = None


class PaperUploadResponse(BaseModel):
    """Response after uploading a paper."""
    paper_id: str
    title: str
    authors: List[str]
    concepts_extracted: List[str]
    message: str


class ResearchQuery(BaseModel):
    """Natural language query from researcher."""
    researcher_id: str
    query: str
    context: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    """Response to a research query."""
    answer: str
    relevant_papers: List[str]
    concepts_used: List[str]
    confidence: float
    sources: List[Dict[str, str]]


class MemoryRecallRequest(BaseModel):
    """Request to recall memories."""
    researcher_id: str
    paper_id: Optional[str] = None
    concept: Optional[str] = None
    time_range: Optional[str] = None


class MemoryRecallResponse(BaseModel):
    """Response with recalled memories."""
    memories: List[Dict[str, Any]]
    total_count: int
    memory_type: str


class HypothesisGenerationRequest(BaseModel):
    """Request to generate research hypotheses."""
    researcher_id: str
    topic: str
    constraints: Optional[List[str]] = None
    num_hypotheses: int = 3


class Hypothesis(BaseModel):
    """A generated research hypothesis."""
    hypothesis_text: str
    supporting_papers: List[str]
    novelty_score: float
    confidence_score: float
    reasoning: str


class HypothesisGenerationResponse(BaseModel):
    """Response with generated hypotheses."""
    hypotheses: List[Hypothesis]
    total_papers_analyzed: int


class GraphConnectionRequest(BaseModel):
    """Request to find connections in knowledge graph."""
    researcher_id: str
    source_concept: str
    target_concept: str
    max_hops: int = 5


class GraphPath(BaseModel):
    """A path in the knowledge graph."""
    nodes: List[str]
    relationships: List[str]
    path_length: int
    relevance_score: float


class GraphConnectionResponse(BaseModel):
    """Response with graph connections."""
    paths: List[GraphPath]
    bridge_concepts: List[str]
    explanation: str


class ResearcherProfile(BaseModel):
    """Profile of a researcher."""
    researcher_id: str
    name: str
    research_interests: List[str]
    papers_read: int = 0
    concepts_learned: int = 0
    hypotheses_generated: int = 0
    created_at: datetime = Field(default_factory=datetime.now)


class Annotation(BaseModel):
    """Annotation made by researcher on a paper."""
    paper_id: str
    researcher_id: str
    text: str
    annotation_type: str  # highlight, note, question
    timestamp: datetime = Field(default_factory=datetime.now)


class ConceptNode(BaseModel):
    """A concept in the knowledge graph."""
    concept_id: str
    name: str
    description: Optional[str] = None
    related_papers: List[str] = Field(default_factory=list)
    frequency: int = 0
