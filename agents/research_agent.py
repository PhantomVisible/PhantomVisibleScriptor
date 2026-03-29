"""
Research Agent for Phantom Visible Scripter
Handles web research and content extraction for YouTube script preparation
"""

import logging
from typing import Dict, List, Any
from tools.search import DuckDuckGoSearch
from utils.ollama_client import OllamaClient

logger = logging.getLogger(__name__)

class ResearchAgent:
    """Agent responsible for researching topics and extracting key information"""
    
    def __init__(self, ollama_client: OllamaClient):
        """
        Initialize Research Agent
        
        Args:
            ollama_client: Configured Ollama client instance
        """
        self.ollama = ollama_client
        self.search_tool = DuckDuckGoSearch()
        
    def research_topic(self, topic: str, max_sources: int = 8) -> Dict[str, Any]:
        """
        Perform comprehensive research on a given topic
        
        Args:
            topic: Topic to research
            max_sources: Maximum number of sources to analyze
            
        Returns:
            Structured research results
        """
        logger.info(f"Starting research on topic: {topic}")
        
        # Step 1: Gather web sources
        search_results = self.search_tool.research_topic(topic, max_sources)
        
        if not search_results['sources']:
            logger.warning("No sources found for research")
            return self._create_empty_research(topic)
        
        # Step 2: Extract and synthesize information
        research_summary = self._synthesize_research(search_results)
        
        # Step 3: Extract key insights
        key_insights = self._extract_key_insights(research_summary)
        
        return {
            "topic": topic,
            "research_summary": research_summary,
            "key_insights": key_insights,
            "sources": search_results['sources'],
            "total_sources": len(search_results['sources'])
        }
    
    def _create_empty_research(self, topic: str) -> Dict[str, Any]:
        """Create empty research structure when no sources are found"""
        return {
            "topic": topic,
            "research_summary": f"No research sources found for topic: {topic}",
            "key_insights": {
                "main_points": [],
                "interesting_angles": [],
                "examples": [],
                "statistics": []
            },
            "sources": [],
            "total_sources": 0
        }
    
    def _synthesize_research(self, search_results: Dict[str, Any]) -> str:
        """
        Synthesize research from multiple sources into a coherent summary
        
        Args:
            search_results: Raw search results from DuckDuckGo
            
        Returns:
            Synthesized research summary
        """
        # Prepare source content for analysis
        source_texts = []
        for i, source in enumerate(search_results['sources'][:5]):  # Limit to top 5 for context
            source_text = f"""
Source {i+1}: {source['title']}
URL: {source['url']}
Content: {source['content'][:1000]}  # Limit content length
"""
            source_texts.append(source_text)
        
        all_sources = "\n".join(source_texts)
        
        # Create synthesis prompt
        system_prompt = """You are a research analyst specializing in content creation for YouTube videos. 
Your task is to synthesize information from multiple sources into a comprehensive, well-structured summary.
Focus on extracting the most relevant and interesting information that would be valuable for creating engaging content."""

        prompt = f"""
Please synthesize the following research sources about "{search_results['topic']}' into a comprehensive summary.

{all_sources}

Provide a well-structured summary that includes:
1. Main concepts and definitions
2. Key findings and insights
3. Different perspectives or viewpoints
4. Notable examples or case studies
5. Current trends or developments

Format the summary clearly with headings and bullet points where appropriate.
"""
        
        try:
            return self.ollama.generate_response(prompt, system_prompt)
        except Exception as e:
            logger.error(f"Failed to synthesize research: {e}")
            return f"Error synthesizing research: {str(e)}"
    
    def _extract_key_insights(self, research_summary: str) -> Dict[str, List[str]]:
        """
        Extract key insights from research summary
        
        Args:
            research_summary: Synthesized research summary
            
        Returns:
            Structured key insights
        """
        system_prompt = """You are a content strategist helping create YouTube videos. 
Extract the most valuable insights from research that would help create engaging content."""

        prompt = f"""
Based on the following research summary, extract key insights organized into specific categories.

Research Summary:
{research_summary}

Please provide the following categories with specific, actionable insights:

1. MAIN_POINTS: 3-5 core ideas that must be covered
2. INTERESTING_ANGLES: 3-5 unique perspectives or hooks
3. EXAMPLES: 3-5 concrete examples or stories
4. STATISTICS: Any notable numbers, data, or statistics
5. CONTROVERSIES: Any debates or differing viewpoints

Format your response as:
MAIN_POINTS:
- Point 1
- Point 2
- Point 3

INTERESTING_ANGLES:
- Angle 1
- Angle 2
- Angle 3

EXAMPLES:
- Example 1
- Example 2
- Example 3

STATISTICS:
- Stat 1
- Stat 2

CONTROVERSIES:
- Controversy 1
- Controversy 2
"""
        
        try:
            response = self.ollama.generate_response(prompt, system_prompt)
            return self._parse_insights_response(response)
        except Exception as e:
            logger.error(f"Failed to extract key insights: {e}")
            return {
                "main_points": [],
                "interesting_angles": [],
                "examples": [],
                "statistics": [],
                "controversies": []
            }
    
    def _parse_insights_response(self, response: str) -> Dict[str, List[str]]:
        """Parse the structured insights response"""
        insights = {
            "main_points": [],
            "interesting_angles": [],
            "examples": [],
            "statistics": [],
            "controversies": []
        }
        
        current_category = None
        
        for line in response.split('\n'):
            line = line.strip()
            
            # Check for category headers
            if line.upper().startswith('MAIN_POINTS'):
                current_category = "main_points"
            elif line.upper().startswith('INTERESTING_ANGLES'):
                current_category = "interesting_angles"
            elif line.upper().startswith('EXAMPLES'):
                current_category = "examples"
            elif line.upper().startswith('STATISTICS'):
                current_category = "statistics"
            elif line.upper().startswith('CONTROVERSIES'):
                current_category = "controversies"
            # Check for bullet points
            elif line.startswith('-') and current_category:
                insight = line[1:].strip()
                if insight and current_category in insights:
                    insights[current_category].append(insight)
        
        return insights
