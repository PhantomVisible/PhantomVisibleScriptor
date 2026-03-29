"""
DuckDuckGo search tool for Phantom Visible Scripter
Provides web search capabilities without requiring API keys
"""

import requests
import re
import time
from typing import List, Dict, Any
from urllib.parse import quote, urlparse
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class DuckDuckGoSearch:
    """DuckDuckGo search implementation for web research"""
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.base_url = "https://duckduckgo.com/html/"
    
    def search(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """
        Perform a DuckDuckGo search
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of search results with title, url, and snippet
        """
        try:
            params = {
                'q': query,
                'kl': 'us-en'
            }
            
            response = self.session.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()
            
            return self._parse_results(response.text, max_results)
            
        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
            return []
    
    def _parse_results(self, html_content: str, max_results: int) -> List[Dict[str, Any]]:
        """Parse DuckDuckGo HTML results"""
        soup = BeautifulSoup(html_content, 'html.parser')
        results = []
        
        # Find result divs
        result_divs = soup.find_all('div', class_='result')
        
        for i, result_div in enumerate(result_divs[:max_results]):
            try:
                # Extract title and URL
                title_link = result_div.find('a', class_='result__a')
                if not title_link:
                    continue
                
                title = title_link.get_text(strip=True)
                url = title_link.get('href', '')
                
                # Clean URL (DuckDuckGo sometimes uses redirect URLs)
                if url.startswith('/l/?uddg='):
                    # Extract actual URL from redirect
                    url = url.split('uddg=')[1].split('&')[0]
                    url = requests.utils.unquote(url)
                
                # Extract snippet
                snippet_div = result_div.find('a', class_='result__snippet')
                snippet = snippet_div.get_text(strip=True) if snippet_div else ""
                
                if title and url:
                    results.append({
                        'title': title,
                        'url': url,
                        'snippet': snippet,
                        'position': i + 1
                    })
                    
            except Exception as e:
                logger.warning(f"Failed to parse result {i}: {e}")
                continue
        
        return results
    
    def get_page_content(self, url: str, max_length: int = 5000) -> str:
        """
        Fetch and extract text content from a URL
        
        Args:
            url: URL to fetch
            max_length: Maximum length of content to return
            
        Returns:
            Extracted text content
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Limit length
            if len(text) > max_length:
                text = text[:max_length] + "..."
            
            return text
            
        except Exception as e:
            logger.error(f"Failed to fetch content from {url}: {e}")
            return ""
    
    def research_topic(self, topic: str, max_sources: int = 8) -> Dict[str, Any]:
        """
        Perform comprehensive research on a topic
        
        Args:
            topic: Topic to research
            max_sources: Maximum number of sources to analyze
            
        Returns:
            Research results with summaries and sources
        """
        logger.info(f"Starting research on topic: {topic}")
        
        # Perform initial search
        search_results = self.search(topic, max_results=max_sources)
        
        if not search_results:
            logger.warning("No search results found")
            return {"topic": topic, "sources": [], "summary": ""}
        
        # Fetch content from top sources
        detailed_sources = []
        
        for result in search_results[:max_sources]:
            content = self.get_page_content(result['url'])
            
            if content:
                detailed_sources.append({
                    'title': result['title'],
                    'url': result['url'],
                    'snippet': result['snippet'],
                    'content': content[:2000]  # Limit content length
                })
            
            # Small delay to be respectful
            time.sleep(0.5)
        
        return {
            "topic": topic,
            "query": topic,
            "sources": detailed_sources,
            "total_results": len(search_results)
        }
