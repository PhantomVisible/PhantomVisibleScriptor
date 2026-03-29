"""
Critic Agent for Phantom Visible Scripter
Provides deterministic, professional YouTube script evaluation
"""

import os
import logging
import re
from typing import Dict, Any, Optional
from pathlib import Path

from utils.ollama_client import OllamaClient

logger = logging.getLogger(__name__)

class CriticAgent:
    """
    Professional YouTube script critic focused on engagement and retention.
    
    Provides deterministic, structured feedback for script improvement
    with emphasis on viewer retention and content quality.
    """
    
    def __init__(self, ollama_client: OllamaClient):
        """
        Initialize CriticAgent with OllamaClient
        
        Args:
            ollama_client: Configured OllamaClient instance
        """
        self.ollama = ollama_client
        self._prompt_template = None
        self._load_prompt_template()
        
        # Critic LLM parameters for deterministic behavior
        self.critic_temperature = 0.2  # Low for consistency
        self.critic_top_p = 0.8
        self.critic_top_k = 30
    
    def _load_prompt_template(self) -> None:
        """Load critic prompt template with robust path handling"""
        try:
            # Get absolute project root path
            project_root = Path(__file__).parent.parent
            prompt_path = project_root / "prompts" / "critic_prompt.txt"
            
            if not prompt_path.exists():
                raise FileNotFoundError(f"Critic prompt not found at: {prompt_path}")
            
            with open(prompt_path, "r", encoding="utf-8") as f:
                self._prompt_template = f.read()
                
            logger.info(f"Loaded critic prompt from: {prompt_path}")
            
        except Exception as e:
            logger.error(f"Failed to load critic prompt: {e}")
            raise FileNotFoundError(f"Critical: Could not load critic prompt from {prompt_path}. Please ensure prompts/critic_prompt.txt exists.")
    
    def critique(self, topic: str, plan: str, script: str) -> str:
        """
        Perform comprehensive script critique
        
        Args:
            topic: Script topic
            plan: Content plan (as string)
            script: Full script text
            
        Returns:
            Detailed critic review and feedback
        """
        logger.info(f"Starting critique for topic: {topic}")
        
        try:
            # Validate inputs
            if not all([topic.strip(), plan.strip(), script.strip()]):
                raise ValueError("Topic, plan, and script must be non-empty")
            
            # Format prompt
            prompt = self._prompt_template.format(
                topic=topic,
                plan=plan,
                script=script
            )
            
            # Minimal system prompt - let the file do the heavy lifting
            system_prompt = "You are a strict YouTube script critic focused on engagement and retention."
            
            # Generate response with deterministic parameters
            response = self.ollama.generate_response_with_params(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=self.critic_temperature,
                top_p=self.critic_top_p,
                top_k=self.critic_top_k
            )
            
            logger.info("Critic review completed successfully")
            return response
            
        except Exception as e:
            logger.error(f"Critique failed: {e}")
            return f"Error generating critic review: {str(e)}"
    
    def score_only(self, topic: str, plan: str, script: str) -> Dict[str, Any]:
        """
        Return structured scores only (bonus method for automation)
        
        Args:
            topic: Script topic
            plan: Content plan (as string)  
            script: Full script text
            
        Returns:
            Dictionary with structured scores and metrics
        """
        logger.info(f"Generating score-only critique for: {topic}")
        
        try:
            # Focused scoring prompt
            scoring_prompt = f"""
Analyze this YouTube script and provide ONLY structured scores.

TOPIC: {topic}
SCRIPT: {script}

Return scores 1-10 for:
- Hook: [X/10]
- Clarity: [X/10] 
- Engagement: [X/10]
- Authenticity: [X/10]
- Structure: [X/10]
- Value: [X/10]

Overall: [X/10]

No explanations, just scores.
"""
            
            system_prompt = "You are a YouTube content analyst providing numerical scores only."
            
            response = self.ollama.generate_response_with_params(
                prompt=scoring_prompt,
                system_prompt=system_prompt,
                temperature=0.1,  # Even lower for scoring
                top_p=0.7,
                top_k=20
            )
            
            # Parse scores from response
            scores = self._parse_scores(response)
            logger.info(f"Score-only critique completed: {scores.get('overall', 'N/A')}/10")
            
            return scores
            
        except Exception as e:
            logger.error(f"Score-only critique failed: {e}")
            return {
                "error": str(e),
                "hook": 0,
                "clarity": 0, 
                "engagement": 0,
                "authenticity": 0,
                "structure": 0,
                "value": 0,
                "overall": 0
            }
    
    def _parse_scores(self, response: str) -> Dict[str, Any]:
        """Parse numerical scores from response"""
        scores = {
            "hook": 0,
            "clarity": 0,
            "engagement": 0, 
            "authenticity": 0,
            "structure": 0,
            "value": 0,
            "overall": 0
        }
        
        try:
            # Extract scores using regex
            patterns = {
                "hook": r"Hook:\s*(\d+)/10",
                "clarity": r"Clarity:\s*(\d+)/10", 
                "engagement": r"Engagement:\s*(\d+)/10",
                "authenticity": r"Authenticity:\s*(\d+)/10",
                "structure": r"Structure:\s*(\d+)/10",
                "value": r"Value:\s*(\d+)/10",
                "overall": r"Overall:\s*(\d+)/10"
            }
            
            for key, pattern in patterns.items():
                match = re.search(pattern, response, re.IGNORECASE)
                if match:
                    scores[key] = int(match.group(1))
                else:
                    # Fallback: find any number/10 pattern
                    fallback_match = re.search(rf"{key}.*?(\d+)/10", response, re.IGNORECASE)
                    if fallback_match:
                        scores[key] = int(fallback_match.group(1))
            
        except Exception as e:
            logger.warning(f"Score parsing failed: {e}")
        
        return scores
    
    def get_config(self) -> Dict[str, Any]:
        """Get critic agent configuration"""
        return {
            "temperature": self.critic_temperature,
            "top_p": self.critic_top_p,
            "top_k": self.critic_top_k,
            "prompt_loaded": self._prompt_template is not None
        }