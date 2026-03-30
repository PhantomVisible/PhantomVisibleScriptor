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
        
        # Step 1: Analyze topic complexity and break down if needed
        search_queries = self._analyze_topic_complexity(topic)
        
        all_sources = []
        all_research_summaries = []
        
        # Step 2: Perform multiple searches for complex topics
        for i, query in enumerate(search_queries, 1):
            logger.info(f"Search {i}/{len(search_queries)}: {query}")
            
            # Gather web sources for this sub-topic
            search_results = self.search_tool.research_topic(query, max_sources // len(search_queries))
            
            if search_results['sources']:
                # Extract and synthesize information for this sub-topic
                research_summary = self._synthesize_research(search_results)
                all_research_summaries.append(research_summary)
                all_sources.extend(search_results['sources'])
        
        # Step 3: Combine all research into comprehensive summary
        combined_summary = self._combine_research_summaries(all_research_summaries, search_queries)
        
        # Step 4: Extract key insights from combined research
        key_insights = self._extract_key_insights(combined_summary)
        
        return {
            "topic": topic,
            "research_summary": combined_summary,
            "key_insights": key_insights,
            "sources": all_sources,
            "total_sources": len(all_sources),
            "search_queries_used": search_queries  # Track what was searched
        }
    
    def _analyze_topic_complexity(self, topic: str) -> List[str]:
        """
        Analyze topic complexity and break down into searchable components
        
        Args:
            topic: Complex topic to analyze
            
        Returns:
            List of search queries for different aspects
        """
        # Check if topic is complex (multiple concepts, specific details, etc.)
        complexity_indicators = [
            " and ", " or ", " vs ", " versus ", " compared to ",
            " how to ", " what is ", " why does ", " when should ",
            " benefits of ", " drawbacks of ", " advantages ", " disadvantages ",
            " history of ", " evolution of ", " future of ",
            " types of ", " kinds of ", " categories of ",
            " examples of ", " case study ", " research on ",
            " analysis of ", " explanation of ", " definition of "
        ]
        
        # If topic appears complex, break it down
        if any(indicator in topic.lower() for indicator in complexity_indicators):
            return self._break_down_complex_topic(topic)
        
        # For simple topics, return as-is
        return [topic]
    
    def _break_down_complex_topic(self, topic: str) -> List[str]:
        """
        Break down complex topic into multiple search queries
        
        Args:
            topic: Complex topic to break down
            
        Returns:
            List of focused search queries
        """
        queries = []
        
        # Handle YouTube script topics specifically
        if "YouTube video essay script" in topic or "script that uses" in topic or "Counter mechanic" in topic:
            # Extract the core subject from various YouTube script topics
            topic_lower = topic.lower()
            
            if "counter mechanic" in topic_lower and "batman" in topic_lower:
                queries.append("Batman: Arkham Knight Counter mechanic")
                queries.append("Freeflow combat system Batman")
                queries.append("focus and momentum psychology")
                queries.append("distraction counter techniques")
                queries.append("deep work productivity")
            elif "first strike" in topic_lower and "executive dysfunction" in topic_lower:
                queries.append("Executive Dysfunction")
                queries.append("First Strike momentum")
                queries.append("5-Minute Rule productivity")
                queries.append("psychological flow state")
                queries.append("procrastination techniques")
            else:
                # Generic YouTube topic extraction
                # Look for quoted terms or key concepts
                import re
                quoted_terms = re.findall(r'"([^"]+)"', topic)
                if quoted_terms:
                    queries.extend(quoted_terms[:3])
                else:
                    # Extract key phrases
                    words = topic.split()
                    key_concepts = []
                    for i in range(len(words)-1):
                        phrase = f"{words[i]} {words[i+1]}"
                        if len(phrase) > 5 and any(keyword in phrase.lower() for keyword in ['mechanic', 'system', 'technique', 'method', 'strategy']):
                            key_concepts.append(phrase)
                    queries.extend(key_concepts[:3])
        
        # Extract main topic and sub-components
        elif ":" in topic:
            # Format like "Main Topic: Sub-Topic"
            main_topic = topic.split(":")[0].strip()
            sub_topic = topic.split(":")[1].strip()
            queries.append(main_topic)  # Search for main topic
            queries.append(sub_topic)  # Search for sub-topic
        elif "The " in topic:
            # Handle "The X of Y" format
            remaining = topic.replace("The ", "").replace(" of ", "")
            if " and " in remaining:
                components = remaining.split(" and ")
                queries.extend(components)  # Search each component
            else:
                queries.append(remaining)  # Search the remaining phrase
        elif "(" in topic and ")" in topic:
            # Handle parenthetical topics
            base_topic = topic.split("(")[0].strip()
            queries.append(base_topic)
            # Extract content in parentheses
            parenthetical = topic[topic.find("(")+1:topic.find(")")].strip()
            if parenthetical:
                queries.append(parenthetical)
        else:
            # For other complex topics, try to identify key concepts
            words = topic.split()
            if len(words) > 5:  # Long topics might be complex
                # Search for key phrases
                key_phrases = []
                for i in range(0, len(words), 2):
                    phrase = " ".join(words[i:i+2])
                    if len(phrase) > 3:  # Only meaningful phrases
                        key_phrases.append(phrase)
                queries.extend(key_phrases[:3])  # Top 3 key phrases
            else:
                queries.append(topic)  # Simple topic, search as-is
        
        # Remove duplicates while preserving order
        seen = set()
        unique_queries = []
        for query in queries:
            if query.lower() not in seen and len(query.strip()) > 3:
                seen.add(query.lower())
                unique_queries.append(query.strip())
        
        logger.info(f"Topic analysis: {len(unique_queries)} search queries from topic: {topic}")
        return unique_queries[:5]  # Limit to 5 most relevant queries
    
    def _combine_research_summaries(self, research_summaries: List[str], search_queries: List[str]) -> str:
        """
        Combine multiple research summaries into comprehensive overview
        
        Args:
            research_summaries: List of research summaries from different queries
            search_queries: List of queries that were searched
            
        Returns:
            Combined research summary
        """
        if len(research_summaries) == 1:
            return research_summaries[0]  # Single search, return as-is
        
        # Create combined summary
        combined_parts = []
        combined_parts.append("COMPREHENSIVE RESEARCH SUMMARY")
        combined_parts.append(f"Based on {len(search_queries)} focused searches:")
        
        for i, (query, summary) in enumerate(zip(search_queries, research_summaries), 1):
            combined_parts.append(f"\n{i}. {query}:")
            combined_parts.append(f"{summary}")
        
        return "\n".join(combined_parts)
    
    def get_sources_report(self, research_data: Dict[str, Any]) -> str:
        """
        Generate a transparent report of all sources used in research
        
        Args:
            research_data: Research results from research_topic()
            
        Returns:
            Formatted string listing all sources with URLs
        """
        sources = research_data.get('sources', [])
        
        if not sources:
            return "🔍 **No sources were used for this research**"
        
        report = "📚 **Sources Used in Research:**\n\n"
        
        for i, source in enumerate(sources, 1):
            report += f"**{i}. {source.get('title', 'Unknown Title')}**\n"
            report += f"   🔗 URL: {source.get('url', 'No URL')}\n"
            report += f"   📝 Snippet: {source.get('content', 'No content')[:100]}...\n\n"
        
        report += f"📊 **Total Sources:** {len(sources)}\n"
        report += "⚠️ **Note:** These sources were found via DuckDuckGo search and used to generate the research summary."
        
        return report
    
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
Content: {source['content'][:500]}...
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
2. Key examples and case studies
3. Statistics and data points
4. Interesting angles or perspectives
5. Contrasting viewpoints if applicable

Format the summary clearly with headings and bullet points for easy reading.
"""
        
        try:
            response = self.ollama.generate_response(prompt, system_prompt)
            return response
        except Exception as e:
            logger.error(f"Failed to synthesize research: {e}")
            return f"Failed to synthesize research: {e}"
    
    def _extract_key_insights(self, research_summary: str) -> Dict[str, Any]:
        """
        Extract key insights from synthesized research summary
        
        Args:
            research_summary: Synthesized research summary
            
        Returns:
            Structured key insights
        """
        # Extract main points, examples, statistics, interesting angles
        main_points = []
        examples = []
        statistics = []
        interesting_angles = []
        
        lines = research_summary.split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('Main concepts:'):
                current_section = 'main_points'
                main_points.append(line.replace('Main concepts:', '').strip())
            elif line.startswith('Key examples:'):
                current_section = 'examples'
                examples.append(line.replace('Key examples:', '').strip())
            elif line.startswith('Statistics:'):
                current_section = 'statistics'
                statistics.append(line.replace('Statistics:', '').strip())
            elif line.startswith('Interesting angles:'):
                current_section = 'interesting_angles'
                interesting_angles.append(line.replace('Interesting angles:', '').strip())
        
        return {
            "main_points": main_points,
            "examples": examples,
            "statistics": statistics,
            "interesting_angles": interesting_angles
        }
