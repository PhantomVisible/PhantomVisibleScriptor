"""
Ollama client utility for Phantom Visible Scripter
Handles communication with local Ollama instance using LangChain
"""

from langchain_community.llms import Ollama
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.chat_models import ChatOllama
import logging
from typing import List, Dict, Any

logger = logging.getLogger(__name__)

class OllamaClient:
    """Client for interacting with local Ollama instance"""
    
    def __init__(self, model_name: str = "llama3.1:8b", base_url: str = "http://localhost:11434"):
        """
        Initialize Ollama client
        
        Args:
            model_name: Name of the model to use (default: llama3.1:8b)
            base_url: Base URL for Ollama instance
        """
        self.model_name = model_name
        self.base_url = base_url
        self.llm = ChatOllama(
            model=model_name,
            base_url=base_url,
            temperature=0.7,
            top_p=0.9,
            top_k=40
        )
        
    def test_connection(self) -> bool:
        """Test connection to Ollama instance"""
        try:
            response = self.llm.invoke("Hello, are you working?")
            return bool(response.content)
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            return False
    
    def generate_response(self, prompt: str, system_prompt: str = None) -> str:
        """
        Generate response from Ollama
        
        Args:
            prompt: The main prompt to send
            system_prompt: Optional system prompt for context
            
        Returns:
            Generated text response
        """
        try:
            messages = []
            
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            
            messages.append(HumanMessage(content=prompt))
            
            response = self.llm.invoke(messages)
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            raise
    
    def generate_structured_response(self, prompt: str, system_prompt: str = None) -> Dict[str, Any]:
        """
        Generate structured response (for JSON-like outputs)
        
        Args:
            prompt: The main prompt to send
            system_prompt: Optional system prompt for context
            
        Returns:
            Parsed response as dictionary
        """
        try:
            # Add instruction for structured output
            structured_prompt = f"{prompt}\n\nPlease respond in a structured, clear format."
            
            response = self.generate_response(structured_prompt, system_prompt)
            
            # Simple parsing - in production, you might want more sophisticated parsing
            return {"response": response}
            
        except Exception as e:
            logger.error(f"Error generating structured response: {e}")
            raise
    
    def generate_response_with_params(self, prompt: str, system_prompt: str = None, temperature: float = 0.7, top_p: float = 0.9, top_k: int = 40) -> str:
        """
        Generate response from Ollama with custom parameters
        
        Args:
            prompt: The main prompt to send
            system_prompt: Optional system prompt for context
            temperature: Sampling temperature (0.0-1.0)
            top_p: Nucleus sampling parameter
            top_k: Top-k sampling parameter
            
        Returns:
            Generated text response
        """
        try:
            # Create temporary LLM with custom parameters
            temp_llm = ChatOllama(
                model=self.model_name,
                base_url=self.base_url,
                temperature=temperature,
                top_p=top_p,
                top_k=top_k
            )
            
            messages = []
            
            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))
            
            messages.append(HumanMessage(content=prompt))
            
            response = temp_llm.invoke(messages)
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"Error generating response with custom params: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model"""
        return {
            "model_name": self.model_name,
            "base_url": self.base_url,
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40
        }
