"""
Planning Agent for Phantom Visible Scripter
Creates structured content plans based on research findings
"""

import logging
from typing import Dict, List, Any
from utils.ollama_client import OllamaClient

logger = logging.getLogger(__name__)

class PlanningAgent:
    """Agent responsible for creating structured content plans"""
    
    def __init__(self, ollama_client: OllamaClient):
        """
        Initialize Planning Agent
        
        Args:
            ollama_client: Configured Ollama client instance
        """
        self.ollama = ollama_client
    
    def create_content_plan(self, research_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a structured content plan based on research findings
        
        Args:
            research_data: Research results from ResearchAgent
            
        Returns:
            Structured content plan
        """
        logger.info(f"Creating content plan for topic: {research_data['topic']}")
        
        # Generate hook ideas
        hooks = self._generate_hooks(research_data)
        
        # Create main sections
        sections = self._create_sections(research_data)
        
        # Design narrative flow
        narrative_flow = self._design_narrative_flow(research_data, hooks, sections)
        
        # Estimate video structure
        video_structure = self._estimate_video_structure(narrative_flow)
        
        return {
            "topic": research_data['topic'],
            "hooks": hooks,
            "sections": sections,
            "narrative_flow": narrative_flow,
            "video_structure": video_structure,
            "estimated_length": video_structure['estimated_duration'],
            "target_word_count": video_structure['target_word_count']
        }
    
    def _generate_hooks(self, research_data: Dict[str, Any]) -> List[str]:
        """Generate compelling hook ideas based on research"""
        
        system_prompt = """You are a YouTube content strategist specializing in creating viral hooks. 
Your task is to create compelling opening hooks that grab attention immediately."""

        # Prepare research context
        key_insights = research_data.get('key_insights', {})
        main_points = key_insights.get('main_points', [])
        interesting_angles = key_insights.get('interesting_angles', [])
        
        context = f"""
Topic: {research_data['topic']}

Main Points:
{chr(10).join(f"- {point}" for point in main_points[:3])}

Interesting Angles:
{chr(10).join(f"- {angle}" for angle in interesting_angles[:3])}

Research Summary Preview:
{research_data.get('research_summary', '')[:500]}...
"""
        
        prompt = f"""
Based on the following research context, generate 5 compelling hooks for a YouTube video about "{research_data['topic']}".

{context}

Each hook should:
- Be 15-25 words long
- Create curiosity or surprise
- Be conversational and engaging
- Avoid being clickbait but still compelling
- Set up the video's main premise

Format your response as a numbered list:
1. [Hook 1]
2. [Hook 2]
3. [Hook 3]
4. [Hook 4]
5. [Hook 5]
"""
        
        try:
            response = self.ollama.generate_response(prompt, system_prompt)
            return self._parse_numbered_list(response)
        except Exception as e:
            logger.error(f"Failed to generate hooks: {e}")
            return ["Failed to generate hooks"]
    
    def _create_sections(self, research_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create main content sections based on research"""
        
        system_prompt = """You are an educational content creator who structures information for maximum engagement and clarity.
Your task is to organize research into logical, engaging video sections."""

        key_insights = research_data.get('key_insights', {})
        examples = key_insights.get('examples', [])
        statistics = key_insights.get('statistics', [])
        
        context = f"""
Topic: {research_data['topic']}

Key Points:
{chr(10).join(f"- {point}" for point in key_insights.get('main_points', []))}

Examples Available:
{chr(10).join(f"- {example}" for example in examples[:5])}

Statistics/Data:
{chr(10).join(f"- {stat}" for stat in statistics[:3])}
"""
        
        prompt = f"""
Based on the research context, create 4-5 logical sections for a 10-15 minute YouTube video about "{research_data['topic']}".

{context}

For each section, provide:
1. A clear, engaging title
2. The main purpose/goal of this section
3. Key points to cover
4. Estimated duration (in minutes)

Format as:
SECTION 1:
Title: [Section Title]
Purpose: [What this section accomplishes]
Key Points:
- Point 1
- Point 2
- Point 3
Duration: [X] minutes

[Repeat for each section]
"""
        
        try:
            response = self.ollama.generate_response(prompt, system_prompt)
            parsed_sections = self._parse_sections(response)
            
            # If no sections were parsed, create default sections
            if not parsed_sections:
                logger.warning("No sections parsed, creating default sections")
                parsed_sections = self._create_default_sections(research_data['topic'])
            
            return parsed_sections
        except Exception as e:
            logger.error(f"Failed to create sections: {e}")
            return self._create_default_sections(research_data['topic'])
    
    def _create_default_sections(self, topic: str) -> List[Dict[str, Any]]:
        """Create default sections for any topic"""
        return [
            {
                'title': 'Introduction & Problem Setup',
                'purpose': 'Introduce the core problem and why it matters',
                'key_points': [
                    'Define the main challenge',
                    'Explain why viewers should care',
                    'Set up the video premise'
                ],
                'duration': 3
            },
            {
                'title': 'The Core Concept',
                'purpose': 'Explain the main theory or framework',
                'key_points': [
                    'Introduce the key concept',
                    'Provide context and background',
                    'Use relatable examples'
                ],
                'duration': 4
            },
            {
                'title': 'Practical Application',
                'purpose': 'Show how to apply the concept in real life',
                'key_points': [
                    'Provide actionable steps',
                    'Share real-world examples',
                    'Address common obstacles'
                ],
                'duration': 4
            },
            {
                'title': 'Conclusion & Call to Action',
                'purpose': 'Summarize key points and motivate action',
                'key_points': [
                    'Recap main takeaways',
                    'Provide clear next steps',
                    'End with motivational message'
                ],
                'duration': 2
            }
        ]
    
    def _design_narrative_flow(self, research_data: Dict[str, Any], hooks: List[str], sections: List[Dict]) -> List[str]:
        """Design the overall narrative flow of the video"""
        
        system_prompt = """You are a storytelling expert who crafts compelling narratives for educational content.
Your task is to create a logical flow that connects all video elements cohesively."""

        # Summarize sections for context
        section_summary = "\n".join([
            f"Section {i+1}: {section['title']} - {section['purpose']}" 
            for i, section in enumerate(sections)
        ])
        
        prompt = f"""
Design a narrative flow for a YouTube video about "{research_data['topic']}".

Available Hooks:
{chr(10).join(f"- {hook}" for hook in hooks[:3])}

Video Sections:
{section_summary}

Create a step-by-step narrative flow that describes:
1. How the video opens (which hook to use)
2. How each section transitions to the next
3. How the video concludes
4. Key storytelling techniques to use

Format as a numbered list of narrative steps:
1. [Opening with hook X]
2. [Transition to Section 1]
3. [Section 1 delivery approach]
4. [Transition to Section 2]
5. [And so on...]
"""
        
        try:
            response = self.ollama.generate_response(prompt, system_prompt)
            return self._parse_numbered_list(response)
        except Exception as e:
            logger.error(f"Failed to design narrative flow: {e}")
            return ["Failed to design narrative flow"]
    
    def _estimate_video_structure(self, narrative_flow: List[str]) -> Dict[str, Any]:
        """Estimate video structure and metrics"""
        
        # Use a fixed minimum section count for better video structure
        section_count = 4  # Minimum 4 sections for good video structure
        
        # Estimate durations
        intro_duration = 1.5  # minutes
        section_duration = 4.0  # minutes per section (increased for longer scripts)
        outro_duration = 1.0  # minutes
        
        estimated_duration = intro_duration + (section_count * section_duration) + outro_duration
        target_word_count = int(estimated_duration * 150)  # ~150 words per minute speaking
        
        return {
            "estimated_duration": estimated_duration,
            "target_word_count": target_word_count,
            "intro_duration": intro_duration,
            "section_duration": section_duration,
            "outro_duration": outro_duration,
            "section_count": section_count
        }
    
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
    
    def _parse_sections(self, response: str) -> List[Dict[str, Any]]:
        """Parse sections from response"""
        sections = []
        current_section = {}
        current_field = None
        
        for line in response.split('\n'):
            line = line.strip()
            
            if line.upper().startswith('SECTION') and ':' in line:
                # Save previous section if exists
                if current_section:
                    sections.append(current_section)
                
                # Start new section
                current_section = {
                    'title': '',
                    'purpose': '',
                    'key_points': [],
                    'duration': 0
                }
                current_field = None
                
            elif line.upper().startswith('TITLE:') and current_section:
                current_section['title'] = line.split(':', 1)[1].strip()
                
            elif line.upper().startswith('PURPOSE:') and current_section:
                current_section['purpose'] = line.split(':', 1)[1].strip()
                
            elif line.upper().startswith('KEY POINTS:') and current_section:
                current_field = 'key_points'
                
            elif line.upper().startswith('DURATION:') and current_section:
                duration_text = line.split(':', 1)[1].strip()
                # Extract number from duration
                import re
                match = re.search(r'(\d+)', duration_text)
                current_section['duration'] = int(match.group(1)) if match else 0
                
            elif line.startswith('-') and current_field == 'key_points' and current_section:
                point = line[1:].strip()
                if point:
                    current_section['key_points'].append(point)
        
        # Add last section
        if current_section:
            sections.append(current_section)
        
        return sections
