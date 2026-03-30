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
            Complete script with metadata including sources used
        """
        logger.info(f"Generating script for topic: {research_data['topic']}")
        
        # Store research sources for transparency
        sources_used = research_data.get('sources', [])
        
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
            "target_word_count": content_plan.get('target_word_count', 2200),
            "sources_used": sources_used,  # Track sources for transparency
            "total_sources": len(sources_used)
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
You avoid cringe phrases, clickbait, and overly salesy language.
You MUST write a substantial script that meets the word count target - no shortcuts."""

        # Prepare comprehensive context with better research integration
        hooks = content_plan.get('hooks', [])
        sections = content_plan.get('sections', [])
        narrative_flow = content_plan.get('narrative_flow', [])
        key_insights = research_data.get('key_insights', {})
        research_summary = research_data.get('research_summary', '')
        sources_used = research_data.get('sources', [])
        
        # Extract specific research details for authenticity
        main_points = key_insights.get('main_points', [])
        examples = key_insights.get('examples', [])
        statistics = key_insights.get('statistics', [])
        
        # Build section summary with more detail
        section_summary = ""
        for i, section in enumerate(sections, 1):
            section_summary += f"""
Section {i}: {section['title']} ({section['duration']} min)
Purpose: {section['purpose']}
Key Points: {', '.join(section.get('key_points', []))}
"""
        
        # Create enhanced context with real research integration
        context = f"""
TOPIC: {research_data['topic']}

TARGET: 10-15 minute video (~{content_plan.get('target_word_count', 2200)} words)
CRITICAL: You MUST write at least {content_plan.get('target_word_count', 2200)} words. Do not stop early.
WARNING: Your word count will be verified after generation. Short scripts will be rejected.

RESEARCH INSIGHTS (Use these in your script):
Main Points: {', '.join(main_points) if main_points else 'No specific main points found'}
Examples: {', '.join(examples) if examples else 'No specific examples found'}
Statistics: {', '.join(statistics) if statistics else 'No specific statistics found'}

DETAILED RESEARCH:
{research_summary}

SOURCES USED ({len(sources_used)} total):
{chr(10).join([f"- {source.get('title', 'Unknown')}: {source.get('url', 'No URL')}" for source in sources_used[:3]])}

CONTENT STRUCTURE:
Hook Options: {', '.join(hooks[:3])}

Sections:
{section_summary}

NARRATIVE FLOW:
{chr(10).join(narrative_flow)}

REQUIREMENTS:
1. Start with the strongest hook from the options
2. Follow the narrative flow naturally
3. Cover all sections in order
4. Include specific examples and statistics from research
5. Maintain a conversational, motivational tone
6. Write for speaking (natural language, not formal writing)
7. Include smooth transitions between sections
8. End with a strong call-to-action and conclusion
9. CRITICAL: Write at least {content_plan.get('target_word_count', 2200)} words - NO SHORTCUTS
10. Avoid clichés and cringe phrases
11. Actually use the research provided - don't just mention it exists
12. Word count will be verified - short scripts will be rejected

Format the script clearly with:
[HOOK] - Opening hook
[TRANSITION] - Section transitions
[EXAMPLE] - When sharing examples
[STATISTIC] - When sharing data
[CONCLUSION] - Closing section

Write the complete script now:
"""
        
        try:
            response = self.ollama.generate_response(context, system_prompt)
            
            # Verify word count immediately after generation
            actual_word_count = self._analyze_script(response)['word_count']
            target_word_count = content_plan.get('target_word_count', 2200)
            
            logger.info(f"Generated script: {actual_word_count} words (target: {target_word_count})")
            
            if actual_word_count < target_word_count * 0.8:  # Allow 80% of target
                logger.error(f"SCRIPT TOO SHORT: {actual_word_count} vs target {target_word_count}")
                # Add instruction to extend the script
                extension_prompt = f"""
CRITICAL: Your script is too short ({actual_word_count} words vs target {target_word_count} words).
This is unacceptable. You MUST extend it by adding more detail, examples, and depth to reach at least {target_word_count} words.

Current script:
{response}

REQUIREMENTS FOR EXTENSION:
1. Add more detailed examples
2. Include specific statistics from research
3. Expand each section with more depth
4. Add personal anecdotes or stories
5. Include more transitions between ideas
6. Reach EXACTLY {target_word_count} words minimum

Please extend the script to meet the word count requirement:
"""
                extended_response = self.ollama.generate_response(extension_prompt, system_prompt)
                
                # Verify the extended script
                extended_word_count = self._analyze_script(extended_response)['word_count']
                logger.info(f"Extended script: {extended_word_count} words (target: {target_word_count})")
                
                if extended_word_count >= target_word_count * 0.8:
                    return extended_response
                else:
                    logger.error(f"EXTENSION FAILED: {extended_word_count} words - still too short")
                    return f"Failed to generate sufficient script length. Got {extended_word_count} words, needed {target_word_count}."
            else:
                return response
        except Exception as e:
            logger.error(f"Failed to generate full script: {e}")
            return "Failed to generate script. Please try again."
    
    def _analyze_script(self, script: str) -> Dict[str, Any]:
        """Analyze script statistics"""
        import re
        
        # Clean script and count words more accurately
        # Remove script markers and formatting
        clean_script = re.sub(r'\[.*?\]', '', script)  # Remove [HOOK], [TRANSITION], etc.
        clean_script = re.sub(r'\*\*.*?\*\*', '', clean_script)  # Remove bold formatting
        clean_script = re.sub(r'\*.*?\*', '', clean_script)  # Remove italic formatting
        clean_script = re.sub(r'---.*?---', '', clean_script)  # Remove separators
        
        # Count words using improved regex
        words = re.findall(r'\b[a-zA-Z]+\b', clean_script)
        word_count = len(words)
        estimated_duration = word_count / 150  # ~150 words per minute
        
        # Log actual word count for verification
        logger.info(f"Script analysis: {word_count} words, {estimated_duration:.1f} minutes")
        
        # Additional verification
        if word_count < 1000:
            logger.warning(f"Script appears short: {word_count} words")
        elif word_count > 5000:
            logger.warning(f"Script appears very long: {word_count} words")
        
        return {
            "word_count": word_count,
            "estimated_duration": estimated_duration,
            "character_count": len(script),
            "paragraph_count": len([p for p in script.split('\n\n') if p.strip()]),
            "clean_word_count": word_count  # Track cleaned word count
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
