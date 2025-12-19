"""
PDF processing service for extracting text and metadata from academic papers.
"""
import PyPDF2
import pdfplumber
import re
import logging
from typing import Dict, List, Optional, Tuple
from io import BytesIO

logger = logging.getLogger(__name__)


class PDFProcessor:
    """Service for processing PDF files and extracting academic content."""
    
    def __init__(self):
        pass
    
    def extract_text(self, pdf_file: BytesIO) -> str:
        """Extract full text from PDF."""
        try:
            text = ""
            with pdfplumber.open(pdf_file) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            # Fallback to PyPDF2
            try:
                pdf_file.seek(0)
                reader = PyPDF2.PdfReader(pdf_file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
                return text
            except Exception as e2:
                logger.error(f"Fallback extraction also failed: {e2}")
                raise
    
    def extract_metadata(self, text: str) -> Dict[str, any]:
        """Extract metadata from paper text."""
        metadata = {
            "title": self._extract_title(text),
            "authors": self._extract_authors(text),
            "abstract": self._extract_abstract(text),
            "year": self._extract_year(text),
            "keywords": self._extract_keywords(text)
        }
        return metadata
    
    def _extract_title(self, text: str) -> Optional[str]:
        """Extract paper title (usually first significant line)."""
        lines = text.split('\n')
        for line in lines[:10]:  # Check first 10 lines
            line = line.strip()
            if len(line) > 20 and len(line) < 200:  # Reasonable title length
                # Remove common header artifacts
                if not any(x in line.lower() for x in ['arxiv', 'preprint', 'submitted', 'page']):
                    return line
        return lines[0].strip() if lines else "Untitled"
    
    def _extract_authors(self, text: str) -> List[str]:
        """Extract author names from paper."""
        authors = []
        
        # Look for common author patterns
        lines = text.split('\n')[:30]  # Check first 30 lines
        
        # Pattern 1: Names followed by affiliations
        author_pattern = r'([A-Z][a-z]+ [A-Z][a-z]+(?:,? (?:and |& )?[A-Z][a-z]+ [A-Z][a-z]+)*)'
        
        for line in lines:
            if 'author' in line.lower() or '@' in line:
                # Extract names
                matches = re.findall(r'[A-Z][a-z]+ [A-Z][a-z]+', line)
                authors.extend(matches)
        
        # Remove duplicates while preserving order
        seen = set()
        unique_authors = []
        for author in authors:
            if author not in seen:
                seen.add(author)
                unique_authors.append(author)
        
        return unique_authors[:10]  # Limit to 10 authors
    
    def _extract_abstract(self, text: str) -> Optional[str]:
        """Extract abstract from paper."""
        # Look for abstract section
        abstract_pattern = r'(?i)abstract\s*[:\-]?\s*(.*?)(?=\n\s*\n|\n(?:1\.|introduction|keywords))'
        match = re.search(abstract_pattern, text, re.DOTALL)
        
        if match:
            abstract = match.group(1).strip()
            # Clean up
            abstract = re.sub(r'\s+', ' ', abstract)
            return abstract[:1000]  # Limit length
        
        return None
    
    def _extract_year(self, text: str) -> Optional[int]:
        """Extract publication year."""
        # Look for 4-digit year in first 500 characters
        year_pattern = r'\b(19|20)\d{2}\b'
        matches = re.findall(year_pattern, text[:500])
        
        if matches:
            # Return most recent year found
            years = [int(y) for y in matches]
            return max(years)
        
        return None
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from paper."""
        keywords = []
        
        # Look for keywords section
        keywords_pattern = r'(?i)keywords?\s*[:\-]?\s*(.*?)(?=\n\s*\n|\n(?:1\.|introduction))'
        match = re.search(keywords_pattern, text, re.DOTALL)
        
        if match:
            keywords_text = match.group(1).strip()
            # Split by common delimiters
            keywords = re.split(r'[,;·•]', keywords_text)
            keywords = [k.strip() for k in keywords if k.strip()]
            keywords = keywords[:10]  # Limit to 10 keywords
        
        return keywords
    
    def extract_sections(self, text: str) -> Dict[str, str]:
        """Extract main sections from paper."""
        sections = {}
        
        # Common section headers
        section_patterns = [
            r'(?i)\n\s*(introduction)\s*\n',
            r'(?i)\n\s*(related work|literature review)\s*\n',
            r'(?i)\n\s*(methodology|methods)\s*\n',
            r'(?i)\n\s*(results)\s*\n',
            r'(?i)\n\s*(discussion)\s*\n',
            r'(?i)\n\s*(conclusion)\s*\n',
            r'(?i)\n\s*(references)\s*\n'
        ]
        
        # Find section boundaries
        section_positions = []
        for pattern in section_patterns:
            match = re.search(pattern, text)
            if match:
                section_positions.append((match.start(), match.group(1)))
        
        # Sort by position
        section_positions.sort()
        
        # Extract section content
        for i, (start, section_name) in enumerate(section_positions):
            end = section_positions[i + 1][0] if i + 1 < len(section_positions) else len(text)
            section_text = text[start:end].strip()
            sections[section_name.lower()] = section_text[:2000]  # Limit section length
        
        return sections
    
    def extract_references(self, text: str) -> List[str]:
        """Extract references from paper."""
        references = []
        
        # Find references section
        ref_pattern = r'(?i)\n\s*references\s*\n(.*?)(?=\n\s*(?:appendix|$))'
        match = re.search(ref_pattern, text, re.DOTALL)
        
        if match:
            ref_text = match.group(1)
            # Split by common reference patterns
            ref_lines = re.split(r'\n\[\d+\]|\n\d+\.', ref_text)
            references = [ref.strip() for ref in ref_lines if len(ref.strip()) > 20]
            references = references[:50]  # Limit to 50 references
        
        return references
    
    def process_pdf(self, pdf_file: BytesIO) -> Dict[str, any]:
        """Process PDF and extract all relevant information."""
        try:
            # Extract full text
            full_text = self.extract_text(pdf_file)
            
            # Extract metadata
            metadata = self.extract_metadata(full_text)
            
            # Extract sections
            sections = self.extract_sections(full_text)
            
            # Extract references
            references = self.extract_references(full_text)
            
            return {
                "full_text": full_text,
                "metadata": metadata,
                "sections": sections,
                "references": references,
                "success": True
            }
        except Exception as e:
            logger.error(f"Error processing PDF: {e}")
            return {
                "success": False,
                "error": str(e)
            }


# Global instance
pdf_processor = PDFProcessor()
