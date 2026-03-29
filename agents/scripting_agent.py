"""
Scripting Agent for Phantom Visible Scripter
Generates complete YouTube scripts based on research and content plans
"""

import logging
from typing import Dict, List, Any
from utils.ollama_client import OllamaClient

logger = logging.getLogger(__name__)

class ScriptingAgent:
    """Agent responsible for generating complete YouTube scripts"""
    
    def __init__(self, ollama_client: OllamaClient):
        """
        Initialize Scripting Agent
        
        Args:
            ollama_client: Configured Ollama client instance
        """
        self.ollama = ollama_client
    
    def generate_script(self, research_data: Dict[str, Any], content_plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a complete YouTube script
        
        Args:
            research_data: Research results from ResearchAgent
            content_plan: Structured content plan from PlanningAgent
            
        Returns:
            Complete script with metadata
        """
        logger.info(f"Generating script for topic: {research_data['topic']}")
        
        # Generate the full script
        full_script = self._generate_full_script(research_data, content_plan)
        
        # Extract script statistics
        script_stats = self._analyze_script(full_script)
        
        # Generate alternative hooks
        alternative_hooks = self._generate_alternative_hooks(content_plan)
        
        # Create talking points summary
        talking_points = self._extract_talking_points(full_script)
        
        return {
            "topic": research_data['topic'],
            "full_script": full_script,
            "word_count": script_stats['word_count'],
            "estimated_duration": script_stats['estimated_duration'],
            "alternative_hooks": alternative_hooks,
            "talking_points": talking_points,
            "target_duration": content_plan.get('estimated_length', 12),
            "target_word_count": content_plan.get('target_word_count', 1800)
        }
    
    def refine_section(self, original_script: str, section_description: str, feedback: str) -> str:
        """
        Refine a specific section of the script based on user feedback
        
        Args:
            original_script: The original full script
            section_description: Description of the section to refine
            feedback: User feedback for improvements
            
        Returns:
            Refined script section
        """
        system_prompt = """You are a professional YouTube script writer who excels at incorporating feedback.
Your task is to refine a script section based on specific user feedback while maintaining the overall tone and flow."""

        prompt = f"""
Please refine the following script section based on the user's feedback.

Original Script:
{original_script}

Section to Refine:
{section_description}

User Feedback:
{feedback}

Please provide the refined section that:
1. Addresses all the user's feedback
2. Maintains a conversational, motivational tone
3. Flows naturally with the surrounding content
4. Keeps the same approximate length
5. Avoids being cringe or overly salesy

Refined Section:
"""
        
        try:
            return self.ollama.generate_response(prompt, system_prompt)
        except Exception as e:
            logger.error(f"Failed to refine section: {e}")
            return "Failed to refine section. Please try again."
    
    def regenerate_hook(self, topic: str, current_hooks: List[str], feedback: str) -> List[str]:
        """
        Generate new hooks based on feedback
        
        Args:
            topic: Video topic
            current_hooks: Current list of hooks
            feedback: User feedback about current hooks
            
        Returns:
            New list of hook options
        """
        system_prompt = """You are a YouTube content strategist who creates compelling hooks.
Based on user feedback, generate new hook options that better match their preferences."""

        current_hooks_text = "\n".join([f"{i+1}. {hook}" for i, hook in enumerate(current_hooks)])
        
        prompt = f"""
Generate 5 new hook options for a YouTube video about "{topic}" based on this feedback:

Current Hooks:
{current_hooks_text}

User Feedback:
{feedback}

The new hooks should:
- Be 15-25 words long
- Address the feedback provided
- Create curiosity and engagement
- Be conversational and authentic
- Set up the video's value proposition

Please provide 5 new hooks as a numbered list:
1. [New Hook 1]
2. [New Hook 2]
3. [New Hook 3]
4. [New Hook 4]
5. [New Hook 5]
"""
        
        try:
            response = self.ollama.generate_response(prompt, system_prompt)
            return self._parse_numbered_list(response)
        except Exception as e:
            logger.error(f"Failed to regenerate hooks: {e}")
            return ["Failed to generate new hooks"]
    
    def _generate_full_script(self, research_data: Dict[str, Any], content_plan: Dict[str, Any]) -> str:
        """Generate the complete YouTube script"""
        
        system_prompt = """You are a professional YouTube script writer who creates engaging, motivational content.
Your scripts are conversational, authentic, and provide real value to viewers.
You avoid cringe phrases, clickbait, and overly salesy language."""

        # Prepare comprehensive context
        hooks = content_plan.get('hooks', [])
        sections = content_plan.get('sections', [])
        narrative_flow = content_plan.get('narrative_flow', [])
        key_insights = research_data.get('key_insights', {})
        
        context = f"""
TOPIC: {research_data['topic']}

TARGET: 10-15 minute video (~{content_plan.get('target_word_count', 1800)} words)

RESEARCH INSIGHTS:
Main Points: {', '.join(key_insights.get('main_points', []))}
Examples: {', '.join(key_insights.get('examples', []))}
Statistics: {', '.join(key_insights.get('statistics', []))}

CONTENT STRUCTURE:
Hook Options: {', '.join(hooks[:3])}

Sections:
{chr(10).join(f"{i+1}. {section.get('title', 'Untitled')} - {section.get('purpose', '')}" for i, section in enumerate(sections))}

Narrative Flow:
{chr(10).join(f"{i+1}. {step}" for i, step in enumerate(narrative_flow[:5]))}
"""
        
        prompt = f"""
Write a complete YouTube script about "{research_data['topic']}" using the following context:

{context}

REQUIREMENTS:
1. Start with the strongest hook from the options
2. Follow the narrative flow naturally
3. Cover all sections in order
4. Include specific examples and statistics from research
5. Maintain a conversational, motivational tone
6. Write for speaking (natural language, not formal writing)
7. Include smooth transitions between sections
8. End with a strong call-to-action and conclusion
9. Target word count: {content_plan.get('target_word_count', 1800)} words
10. Avoid clichés and cringe phrases

Format the script clearly with:
[HOOK] - Opening hook
[TRANSITION] - Section transitions
[EXAMPLE] - When sharing examples
[STATISTIC] - When sharing data
[CONCLUSION] - Closing section

Write the complete script now:
"""
        
        try:
            return self.ollama.generate_response(prompt, system_prompt)
        except Exception as e:
            logger.error(f"Failed to generate full script: {e}")
            return "Failed to generate script. Please try again."
    
    def _analyze_script(self, script: str) -> Dict[str, Any]:
        """Analyze script statistics"""
        word_count = len(script.split())
        estimated_duration = word_count / 150  # ~150 words per minute
        
        return {
            "word_count": word_count,
            "estimated_duration": estimated_duration,
            "character_count": len(script),
            "paragraph_count": len([p for p in script.split('\n\n') if p.strip()])
        }
    
    def _generate_alternative_hooks(self, content_plan: Dict[str, Any]) -> List[str]:
        """Generate alternative hooks for the script"""
        original_hooks = content_plan.get('hooks', [])
        topic = content_plan.get('topic', '')
        
        system_prompt = """You are a YouTube content strategist.
Generate alternative hooks that offer different approaches to the same topic."""
        
        prompt = f"""
Generate 3 alternative hooks for a YouTube video about "{topic}".

Original hooks for reference:
{chr(10).join(f"- {hook}" for hook in original_hooks[:3])}

The alternative hooks should offer different angles:
1. One that's more surprising/shocking
2. One that's more relatable/personal
3. One that's more educational/informative

Each hook should be 15-25 words and conversational.

Format as:
1. [Surprising Hook]
2. [Relatable Hook]
3. [Educational Hook]
"""
        
        try:
            response = self.ollama.generate_response(prompt, system_prompt)
            return self._parse_numbered_list(response)
        except Exception as e:
            logger.error(f"Failed to generate alternative hooks: {e}")
            return []
    
    def _extract_talking_points(self, script: str) -> List[str]:
        """Extract key talking points from the script"""
        
        system_prompt = """You are a content strategist who extracts key talking points from scripts.
Identify the most important points that viewers should remember."""
        
        prompt = f"""
Extract 5-7 key talking points from this YouTube script:

{script[:2000]}...

The talking points should:
- Be the main takeaways viewers should remember
- Be concise and memorable
- Cover the full scope of the video
- Be actionable or thought-provoking

Format as a numbered list:
1. [Talking Point 1]
2. [Talking Point 2]
...
"""
        
        try:
            return self._parse_numbered_list(self.ollama.generate_response(prompt, system_prompt))
        except Exception as e:
            logger.error(f"Failed to extract talking points: {e}")
            return []
    
    def _parse_numbered_list(self, response: str) -> List[str]:
        """Parse numbered list from response"""
        items = []
        for line in response.split('\n'):
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-')):
                # Remove number/bullet and clean up
                clean_line = line
                if '.' in line[:5]:
                    clean_line = line.split('.', 1)[1].strip()
                elif line.startswith('-'):
                    clean_line = line[1:].strip()
                
                if clean_line:
                    items.append(clean_line)
        return items
