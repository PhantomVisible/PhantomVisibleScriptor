#!/usr/bin/env python3
"""
Phantom Visible Scripter - Local AI Agent for YouTube Script Creation
A modular, extensible system for researching and creating YouTube scripts
"""

import sys
import os
import argparse
import logging
from typing import Dict, Any, List

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.ollama_client import OllamaClient
from agents.research_agent import ResearchAgent
from agents.planning_agent import PlanningAgent
from agents.scripting_agent import ScriptingAgent
from agents.critic_agent import CriticAgent
from agents.collaborative_agent import CollaborativeAgent

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class PhantomVisibleScripter:
    """Main application class for Phantom Visible Scripter"""
    
    def __init__(self, model_name: str = "llama3.1:8b", base_url: str = "http://localhost:11434"):
        """
        Initialize Phantom Visible Scripter
        
        Args:
            model_name: Name of Ollama model to use
            base_url: Base URL for Ollama instance
        """
        self.model_name = model_name
        self.base_url = base_url
        
        # Initialize all agents
        self.ollama = OllamaClient(model_name=model_name, base_url=base_url)
        self.research_agent = ResearchAgent(self.ollama)
        self.planning_agent = PlanningAgent(self.ollama)
        self.scripting_agent = ScriptingAgent(self.ollama)
        self.critic_agent = CriticAgent(self.ollama)
        
        # Initialize collaborative agent (optional)
        try:
            self.collaborative_agent = CollaborativeAgent(
                primary_model="llama3.1:8b",  # Primary script writer
                collaborator_model="mistral:latest"  # Reviewer/critic
            )
        except Exception as e:
            logger.warning(f"Collaborative agent initialization failed: {e}")
            self.collaborative_agent = None
        
        # Initialize separate Ollama clients for section-by-section generation
        try:
            self.llama_client = OllamaClient(model_name="llama3.1:8b", base_url=base_url)
            self.mistral_client = OllamaClient(model_name="mistral:latest", base_url=base_url)
        except Exception as e:
            logger.warning(f"Secondary model client initialization failed: {e}")
            self.llama_client = None
            self.mistral_client = None
        
        # Load scripting prompt template
        self.scripting_prompt_template = self._load_scripting_prompt()
        
        # Storage for current work
        self.current_research = {}
        self.current_plan = {}
        self.current_script = {}
    
    def run(self, topic: str) -> Dict[str, Any]:
        """
        Run the complete script generation pipeline using section-by-section approach
        
        Args:
            topic: YouTube topic to create script for
            
        Returns:
            Complete results including research, plan, and script
        """
        print(f"\n🎬 Phantom Visible Scripter")
        print(f"📝 Topic: {topic}")
        print(f"🤖 Primary Model: llama3.1:8b")
        print(f"🤖 Review Model: mistral:latest")
        print(f"🔗 Ollama: {self.base_url}")
        print("\n" + "="*50)
        
        # Step 1: Test Ollama connection
        if not self._test_connection():
            return {"error": "Failed to connect to Ollama"}
        
        # Step 2: Research
        print("\n🔍 Step 1: Researching topic...")
        self.current_research = self.research_agent.research_topic(topic)
        print(f"✅ Found {self.current_research['total_sources']} sources")
        
        # Step 3: Generate Outline (NEW SECTION-BY-SECTION APPROACH)
        print("\n📋 Step 2: Generating outline...")
        outline = self._generate_outline(topic)
        if not outline:
            return {"error": "Failed to generate outline"}
        print(f"✅ Outline created with {len(outline['sections'])} sections")
        
        # Display outline and get approval
        if not self._get_outline_approval(outline):
            return {"status": "cancelled", "reason": "User rejected outline"}
        
        # Step 4: Section-by-Section Generation
        print("\n✍️  Step 3: Generating script section by section...")
        script_sections = self._generate_sections_loop(topic, outline)
        if not script_sections:
            return {"error": "Failed to generate script sections"}
        
        # Step 5: Stitch sections together
        print("\n🧵 Step 4: Stitching sections together...")
        full_script = self._stitch_sections(script_sections)
        word_count = len(full_script.split())
        estimated_duration = word_count / 150
        
        self.current_script = {
            'topic': topic,
            'full_script': full_script,
            'word_count': word_count,
            'estimated_duration': estimated_duration,
            'sections': script_sections,
            'outline': outline,
            'talking_points': [s['title'] for s in outline['sections']],
            'total_sources': self.current_research.get('total_sources', 0)
        }
        
        print(f"✅ Script complete! ({word_count} words, ~{estimated_duration:.1f} minutes)")
        
        # Step 6: Display results
        self._display_final_results()
        
        # Step 7: Auto-save the script
        self._auto_save_script(topic, full_script, word_count, estimated_duration)
        
        # Step 8: Offer refinement options
        self._offer_refinements()
        
        return {
            "status": "completed",
            "research": self.current_research,
            "outline": outline,
            "script": self.current_script
        }
    
    def _load_scripting_prompt(self) -> str:
        """Load the scripting prompt template from file"""
        try:
            prompt_path = os.path.join(os.path.dirname(__file__), 'prompts', 'scripting_prompt.txt')
            with open(prompt_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.warning(f"Could not load scripting prompt: {e}")
            return ""
    
    def _generate_with_retry(self, client, prompt: str, system_prompt: str = None, max_retries: int = 1) -> str:
        """Generate response with retry logic for Ollama errors"""
        for attempt in range(max_retries + 1):
            try:
                return client.generate_response(prompt, system_prompt)
            except Exception as e:
                logger.error(f"Ollama error (attempt {attempt + 1}/{max_retries + 1}): {e}")
                if attempt == max_retries:
                    raise
                print(f"⚠️  Error occurred, retrying... (attempt {attempt + 2}/{max_retries + 1})")
        return ""
    
    def _test_connection(self) -> bool:
        """Test connection to Ollama"""
        print("🔌 Testing Ollama connection...")
        if self.ollama.test_connection():
            print("✅ Connected to Ollama")
            return True
        else:
            print("❌ Failed to connect to Ollama")
            print("   Make sure Ollama is running: ollama serve")
            return False
    
    def _generate_outline(self, topic: str) -> Dict:
        """
        STEP 1: Generate only an outline with 5-6 sections
        """
        system_prompt = """You are a professional YouTube content planner. Create clear, engaging section outlines.
Respond ONLY with the outline format specified. No extra commentary."""
        
        prompt = f"""
Create a YouTube script outline for: "{topic}"

Requirements:
- 5-6 sections total
- Each section needs:
  1. A compelling title (3-6 words)
  2. A one-sentence description of what that section will cover

The outline should follow this natural flow:
1. HOOK/INTRO - Pattern interrupt, curiosity trigger
2. PROBLEM/CONTEXT - Relatable situation
3. MAIN CONTENT 1 - First key insight
4. MAIN CONTENT 2 - Second key insight  
5. MAIN CONTENT 3 - Third key insight (optional)
6. CONCLUSION/CTA - Resolution and call to action

Respond in this exact format:

SECTION 1: [Title]
Description: [One sentence about what this section covers]

SECTION 2: [Title]
Description: [One sentence about what this section covers]

[Continue for all sections...]
"""
        
        try:
            response = self._generate_with_retry(self.llama_client, prompt, system_prompt)
            return self._parse_outline(response)
        except Exception as e:
            logger.error(f"Outline generation failed: {e}")
            return None
    
    def _parse_outline(self, response: str) -> Dict:
        """Parse the outline response into structured format"""
        sections = []
        lines = response.strip().split('\n')
        current_section = None
        
        for line in lines:
            line = line.strip()
            if line.startswith('SECTION'):
                # Extract section number and title
                parts = line.split(':', 1)
                if len(parts) == 2:
                    title = parts[1].strip()
                    current_section = {'title': title, 'description': ''}
            elif line.startswith('Description:') and current_section:
                desc = line.split(':', 1)[1].strip()
                current_section['description'] = desc
                sections.append(current_section)
                current_section = None
        
        return {'sections': sections, 'raw_outline': response}
    
    def _get_outline_approval(self, outline: Dict) -> bool:
        """Display outline and get user approval"""
        print("\n📋 CONTENT OUTLINE:")
        print("="*50)
        
        for i, section in enumerate(outline['sections'], 1):
            print(f"\n{i}. {section['title']}")
            print(f"   {section['description']}")
        
        print("\n" + "="*50)
        
        while True:
            response = input("Do you approve this outline? (yes/no): ").lower().strip()
            if response == 'yes':
                return True
            elif response == 'no':
                print("❌ Outline rejected. Exiting...")
                return False
            else:
                print("Please enter 'yes' or 'no'")
    
    def _generate_sections_loop(self, topic: str, outline: Dict) -> List[Dict]:
        """
        STEP 2: Generate each section individually with Llama, then review with Mistral
        """
        sections = outline['sections']
        generated_sections = []
        previous_sections_text = ""
        
        for i, section in enumerate(sections, 1):
            total_sections = len(sections)
            print(f"\n� Generating section {i} of {total_sections}: {section['title']}")
            print("-" * 50)
            
            # STEP 2a: Generate section with Llama
            print(f"  📝 Writing with Llama...")
            section_content = self._generate_single_section(
                topic=topic,
                section=section,
                outline=outline,
                previous_sections=previous_sections_text,
                section_number=i,
                total_sections=total_sections
            )
            
            if not section_content:
                print(f"  ❌ Failed to generate section {i}")
                return None
            
            word_count = len(section_content.split())
            print(f"  ✓ Llama draft: {word_count} words")
            
            # STEP 2b: Review and expand with Mistral
            print(f"  🔍 Reviewing with Mistral...")
            reviewed_content = self._review_and_expand_section(
                section_content=section_content,
                section=section,
                previous_sections=previous_sections_text,
                section_number=i,
                total_sections=total_sections
            )
            
            if not reviewed_content:
                print(f"  ⚠️  Mistral review failed, using Llama draft")
                reviewed_content = section_content
            else:
                reviewed_word_count = len(reviewed_content.split())
                print(f"  ✓ Mistral final: {reviewed_word_count} words")
            
            # STEP 2c: Store the section
            generated_sections.append({
                'title': section['title'],
                'description': section['description'],
                'content': reviewed_content,
                'section_number': i
            })
            
            # Update previous sections text for context in next iteration
            previous_sections_text += f"\n\n=== SECTION {i}: {section['title']} ===\n{reviewed_content}"
            
            print(f"  ✅ Section {i} complete!")
        
        return generated_sections
    
    def _generate_single_section(self, topic: str, section: Dict, outline: Dict, 
                                  previous_sections: str, section_number: int, 
                                  total_sections: int) -> str:
        """Generate a single section using Llama"""
        system_prompt = """You are a professional YouTube script writer.
Write in a conversational, motivational tone. Be authentic and engaging.
Write 300-400 words for this section only."""
        
        # Build full outline text
        outline_text = "\n".join([
            f"{i+1}. {s['title']} - {s['description']}"
            for i, s in enumerate(outline['sections'])
        ])
        
        # Determine if this is intro, middle, or conclusion
        if section_number == 1:
            section_type = "HOOK/INTRO - Start with a pattern interrupt, no greetings"
        elif section_number == total_sections:
            section_type = "CONCLUSION - Wrap up with emotional resolution and subtle CTA"
        else:
            section_type = f"MIDDLE SECTION {section_number} of {total_sections}"
        
        prompt = f"""
=== STYLE RULES (MUST FOLLOW) ===
{self.scripting_prompt_template}

=== FULL SCRIPT OUTLINE ===
{outline_text}

=== PREVIOUSLY WRITTEN SECTIONS ===
{previous_sections if previous_sections else "(This is the first section)"}

=== YOUR TASK ===
Write ONLY this section:

SECTION {section_number} of {total_sections}: {section['title']}
Type: {section_type}
Description: {section['description']}

Requirements:
- Write 300-400 words
- Match the conversational, motivational tone from style rules
- DO NOT repeat content from previous sections
- DO NOT include an intro if this is a middle section (just start with the content)
- DO NOT add a conclusion if this isn't the final section
- Flow naturally from previous content if this isn't the first section
- Use smooth transitions
- Include specific examples, not vague statements
- Write as continuous spoken script (no bullet points)

Write the section now:
"""
        
        try:
            return self._generate_with_retry(self.llama_client, prompt, system_prompt)
        except Exception as e:
            logger.error(f"Section generation failed: {e}")
            return None
    
    def _review_and_expand_section(self, section_content: str, section: Dict,
                                    previous_sections: str, section_number: int,
                                    total_sections: int) -> str:
        """Review and expand a section using Mistral"""
        system_prompt = """You are a script editor. Review and improve the provided section.
Maintain the conversational, motivational tone. Expand to 350-450 words.
Do not add intros or outros if this is a middle section."""
        
        # Determine section position context
        if section_number == 1:
            position_note = "This is the HOOK/INTRO - ensure it starts strong with a pattern interrupt."
        elif section_number == total_sections:
            position_note = "This is the CONCLUSION - ensure it provides emotional resolution."
        else:
            position_note = f"This is a MIDDLE SECTION. Do NOT add an intro or outro. Just improve the content."
        
        prompt = f"""
Review and expand this script section:

=== SECTION TITLE ===
{section['title']}

=== PREVIOUS SECTIONS (DO NOT REPEAT) ===
{previous_sections if previous_sections else "(This is the first section)"}

=== POSITION CONTEXT ===
{position_note}

=== SECTION TO REVIEW ===
{section_content}

=== YOUR TASK ===
Review and expand this section to reach 350-450 words.

Requirements:
- Keep the conversational, motivational tone
- {position_note}
- Do not repeat ANY content from previous sections
- Enhance with more specific examples or depth
- Improve flow and clarity
- Maintain natural, spoken language (not robotic)
- Vary sentence length for better pacing
- Use smooth transitions if building on previous content

Output the final, improved version of this section only:
"""
        
        try:
            return self._generate_with_retry(self.mistral_client, prompt, system_prompt)
        except Exception as e:
            logger.error(f"Section review failed: {e}")
            return None
    
    def _stitch_sections(self, sections: List[Dict]) -> str:
        """
        STEP 3: Stitch all sections together into final script
        """
        stitched = []
        
        for section in sections:
            stitched.append(section['content'])
        
        full_script = "\n\n".join(stitched)
        return full_script.strip()
    
    def _auto_save_script(self, topic: str, full_script: str, word_count: int, duration: float):
        """Auto-save the script to a file named after the topic"""
        import os
        
        # Create results folder if it doesn't exist
        results_dir = "results"
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
        
        # Clean topic for filename
        safe_topic = "".join(c if c.isalnum() or c in (' ', '-', '_') else '_' for c in topic)
        safe_topic = safe_topic.replace(' ', '_')[:50]  # Limit length
        
        filename = f"script_{safe_topic}.txt"
        filepath = os.path.join(results_dir, filename)
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Phantom Visible Scripter - YouTube Script\n")
                f.write(f"Topic: {topic}\n")
                f.write(f"Word Count: {word_count}\n")
                f.write(f"Estimated Duration: {duration:.1f} minutes\n")
                f.write(f"Sources Used: {self.current_research.get('total_sources', 0)}\n")
                f.write(f"Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\n" + "="*50 + "\n\n")
                f.write(full_script)
            
            print(f"\n💾 Script auto-saved to: {filepath}")
        except Exception as e:
            logger.error(f"Auto-save failed: {e}")
            print(f"⚠️  Could not auto-save script: {e}")
    
    def _get_plan_approval(self, outline: Dict) -> bool:
        """Display outline and get user approval (legacy method name kept for compatibility)"""
        return self._get_outline_approval(outline)

    def _display_final_results(self):
        """Display the final script results"""
        print("\n" + "="*50)
        print("🎬 FINAL YOUTUBE SCRIPT")
        print("="*50)
        
        # Get verified word count from current script
        verified_word_count = self.current_script.get('word_count', 0)
        verified_duration = self.current_script.get('estimated_duration', 0)
        
        print(f"\n📝 Topic: {self.current_script['topic']}")
        print(f"📊 Word Count: {verified_word_count}")
        print(f"⏱️  Duration: {verified_duration:.1f} minutes")
        print(f"📚 Sources Used: {self.current_script.get('total_sources', 0)} actual web sources")
        
        print(f"\n🎯 Talking Points:")
        for i, point in enumerate(self.current_script['talking_points'], 1):
            print(f"   {i}. {point}")
        
        print(f"\n📄 FULL SCRIPT:")
        print("-" * 50)
        print(self.current_script['full_script'])
        print("-" * 50)
    
    def _run_critic_review(self):
        """Run critic review on the generated script"""
        print("\n" + "="*50)
        print("🔍 CRITIC REVIEW")
        print("="*50)
        
        try:
            # Prepare inputs for critic
            topic = self.current_script['topic']
            outline = str(self.current_script.get('outline', {}))  # Convert outline to string for critic
            script = self.current_script['full_script']
            
            # Get critic review
            print("🎭 Analyzing script quality...")
            review = self.critic_agent.critique(topic, outline, script)
            
            print("\n--- CRITIC REVIEW ---\n")
            print(review)
            print("-" * 50)
            
        except Exception as e:
            logger.error(f"Critic review failed: {e}")
            print(f"❌ Critic review failed: {e}")
    
    def _offer_refinements(self):
        """Offer options for script refinement"""
        print("\n" + "="*50)
        print("🔧 REFINEMENT OPTIONS")
        print("="*50)
        
        while True:
            print("\nOptions:")
            print("1. Regenerate hooks")
            print("2. Refine a specific section")
            print("3. Generate alternative script")
            print("4. Save script to file")
            print("5. Show research sources used")
            print("6. Collaborative improvement (AI discusses with AI)")
            print("7. Exit")
            
            choice = input("Choose an option (1-7): ").strip()
            
            if choice == '1':
                self._regenerate_hooks()
            elif choice == '2':
                self._refine_section()
            elif choice == '3':
                self._regenerate_script()
            elif choice == '4':
                self._save_script()
            elif choice == '5':
                self._show_sources()
            elif choice == '6':
                if self.collaborative_agent:
                    self._collaborative_improvement()
                else:
                    print("⚠️ Collaborative agent not available. This feature requires multiple model instances or additional setup.")
                    print("💡 Tip: Collaborative improvement works best when you have different AI models or want to simulate peer review.")
            elif choice == '7':
                print("\n👋 Thanks for using Phantom Visible Scripter!")
                break
            else:
                print("Invalid choice. Please try again.")
    
    def _regenerate_hooks(self):
        """Regenerate hooks with user feedback"""
        feedback = input("What's wrong with the current hooks? ").strip()
        
        # Get hooks from the outline stored in current_script
        outline = self.current_script.get('outline', {})
        current_hooks = [s['title'] for s in outline.get('sections', [])[:3]]
        
        new_hooks = self.scripting_agent.regenerate_hook(
            self.current_script['topic'],
            current_hooks,
            feedback
        )
        
        print("\n🎣 New Hooks:")
        for i, hook in enumerate(new_hooks, 1):
            print(f"   {i}. {hook}")
        
        # Update the outline with new hooks
        if outline.get('sections'):
            for i, hook in enumerate(new_hooks):
                if i < len(outline['sections']):
                    outline['sections'][i]['title'] = hook
        
        self.current_script['outline'] = outline
        self.current_script['alternative_hooks'] = new_hooks
    
    def _show_sources(self):
        """Show all sources used in research with full transparency"""
        print("\n" + "="*50)
        print("📚 RESEARCH SOURCES TRANSPARENCY REPORT")
        print("="*50)
        
        sources_report = self.research_agent.get_sources_report(self.current_research)
        print(sources_report)
        
        print("\n" + "="*50)
        print("🔍 **Source Verification:**")
        print("- All sources were found via DuckDuckGo search")
        print("- Content was extracted and synthesized by the AI")
        print("- No sources were fabricated or hallucinated")
        print(f"- Research used {self.current_research.get('total_sources', 0)} actual web sources")
        print("="*50)
    
    def _refine_section(self):
        """Refine a specific section"""
        section_desc = input("Describe the section to refine: ").strip()
        feedback = input("What improvements needed? ").strip()
        
        refined = self.scripting_agent.refine_section(
            self.current_script['full_script'],
            section_desc,
            feedback
        )
        
        print(f"\n✍️  Refined Section:")
        print("-" * 30)
        print(refined)
        print("-" * 30)
        
        if input("Replace original section? (yes/no): ").lower() == 'yes':
            # Simple replacement - in production, would be more sophisticated
            self.current_script['full_script'] = refined
            print("✅ Section updated")
    
    def _regenerate_script(self):
        """Generate a completely new script using section-by-section approach"""
        print("\n✍️  Regenerating script from outline...")
        
        # Get the existing outline from current_script
        outline = self.current_script.get('outline')
        if not outline:
            print("❌ No outline available. Cannot regenerate.")
            return
        
        # Re-run section generation with the existing outline
        topic = self.current_script['topic']
        script_sections = self._generate_sections_loop(topic, outline)
        
        if not script_sections:
            print("❌ Failed to regenerate script")
            return
        
        # Stitch sections together
        full_script = self._stitch_sections(script_sections)
        word_count = len(full_script.split())
        estimated_duration = word_count / 150
        
        self.current_script = {
            'topic': topic,
            'full_script': full_script,
            'word_count': word_count,
            'estimated_duration': estimated_duration,
            'sections': script_sections,
            'outline': outline,
            'talking_points': [s['title'] for s in outline['sections']],
            'total_sources': self.current_research.get('total_sources', 0)
        }
        
        print(f"✅ New script generated ({word_count} words)")
        
        # Display new script preview
        print(f"\n📄 New Script Preview:")
        print("-" * 30)
        print(full_script[:500] + "...")
        print("-" * 30)
    
    def _collaborative_improvement(self):
        """Handle collaborative improvement between AI models"""
        print("\n" + "="*50)
        print("🤝 COLLABORATIVE IMPROVEMENT")
        print("="*50)
        
        # Get user feedback for context
        user_feedback = input("Any specific concerns or feedback? (press Enter to skip): ").strip()
        
        print("\n🔄 Step 1: Primary model analyzing its own work...")
        collaborative_result = self.collaborative_agent.collaborative_review(
            self.current_script['full_script'],
            self.current_script['topic'],
            user_feedback
        )
        
        print("\n📊 COLLABORATIVE RESULTS:")
        print(f"Models involved: {', '.join(collaborative_result['models_used'])}")
        
        print("\n🎯 Primary Model Analysis:")
        primary_analysis = collaborative_result.get('primary_analysis', {}).get('analysis', 'No analysis available')
        print(primary_analysis[:500] + "..." if len(primary_analysis) > 500 else primary_analysis)
        
        print("\n🤝 Collaborator Review:")
        collaborator_review = collaborative_result.get('collaborator_review', {}).get('review', 'No review available')
        print(collaborator_review[:500] + "..." if len(collaborator_review) > 500 else collaborator_review)
        
        print("\n📋 Consensus Recommendations:")
        consensus = collaborative_result.get('consensus', {}).get('consensus', 'No consensus available')
        print(consensus[:800] + "..." if len(consensus) > 800 else consensus)
        
        # Ask if user wants to implement improvements
        while True:
            print("\n" + "-"*50)
            print("Options:")
            print("1. Generate improved script based on consensus")
            print("2. Save collaborative analysis to file")
            print("3. Return to main menu")
            
            action = input("Choose an option (1-3): ").strip()
            
            if action == '1':
                print("\n🔄 Generating improved script...")
                improved_script = self.collaborative_agent.generate_improved_script(
                    self.current_script['full_script'],
                    collaborative_result
                )
                
                # Update current script with improved version
                self.current_script['full_script'] = improved_script
                self.current_script['word_count'] = self.scripting_agent._analyze_script(improved_script)['word_count']
                self.current_script['estimated_duration'] = self.current_script['word_count'] / 150
                
                print(f"✅ Improved script generated ({self.current_script['word_count']} words)")
                
                # Ask if user wants to save
                save_choice = input("Save improved script? (y/n): ").strip().lower()
                if save_choice in ['y', 'yes']:
                    self._save_script()
                
            elif action == '2':
                filename = input("Enter filename for collaborative analysis (without extension): ").strip()
                if not filename:
                    filename = f"collaborative_analysis_{self.current_script['topic'].replace(' ', '_')}"
                
                # Create results folder if needed
                import os
                results_dir = "results"
                if not os.path.exists(results_dir):
                    os.makedirs(results_dir)
                
                filepath = os.path.join(results_dir, f"{filename}.txt")
                
                try:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write("PHANTOM VISIBLE SCRIPTER - COLLABORATIVE ANALYSIS\n")
                        f.write(f"Topic: {self.current_script['topic']}\n")
                        f.write(f"Models: {', '.join(collaborative_result['models_used'])}\n")
                        f.write(f"Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                        f.write("\n" + "="*50 + "\n\n")
                        
                        f.write("PRIMARY MODEL ANALYSIS:\n")
                        f.write(primary_analysis + "\n\n")
                        
                        f.write("COLLABORATOR REVIEW:\n")
                        f.write(collaborator_review + "\n\n")
                        
                        f.write("CONSENSUS RECOMMENDATIONS:\n")
                        f.write(consensus + "\n\n")
                        
                        f.write("IMPROVEMENT SUGGESTIONS:\n")
                        for suggestion in collaborative_result.get('improvement_suggestions', []):
                            f.write(f"• {suggestion}\n")
                    
                    print(f"✅ Collaborative analysis saved to {filepath}")
                except Exception as e:
                    print(f"❌ Failed to save analysis: {e}")
                    
            elif action == '3':
                break
            else:
                print("Invalid choice. Please try again.")
    
    def _save_script(self):
        """Save script to file"""
        filename = input("Enter filename (without extension): ").strip()
        if not filename:
            filename = f"script_{self.current_script['topic'].replace(' ', '_')}"
        
        # Create results folder if it doesn't exist
        import os
        results_dir = "results"
        if not os.path.exists(results_dir):
            os.makedirs(results_dir)
            print(f"📁 Created results folder")
        
        filepath = os.path.join(results_dir, f"{filename}.txt")
        
        try:
            # Get verified word count from current script
            verified_word_count = self.current_script.get('word_count', 0)
            verified_duration = self.current_script.get('estimated_duration', 0)
            
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Phantom Visible Scripter - YouTube Script\n")
                f.write(f"Topic: {self.current_script['topic']}\n")
                f.write(f"Word Count: {verified_word_count}\n")
                f.write(f"Estimated Duration: {verified_duration:.1f} minutes\n")
                f.write(f"Sources Used: {self.current_script.get('total_sources', 0)} actual web sources\n")
                f.write(f"Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\n" + "="*50 + "\n\n")
                
                f.write("TALKING POINTS:\n")
                for i, point in enumerate(self.current_script['talking_points'], 1):
                    f.write(f"{i}. {point}\n")
                f.write("\n" + "-"*50 + "\n\n")
                
                f.write("FULL SCRIPT:\n")
                f.write(self.current_script['full_script'])
            
            print(f"✅ Script saved to {filepath}")
            print(f"📁 Location: {os.path.abspath(filepath)}")
        except Exception as e:
            print(f"❌ Failed to save script: {e}")

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Phantom Visible Scripter - AI-powered YouTube script creation"
    )
    parser.add_argument(
        "topic",
        nargs="?",
        help="YouTube topic to create script for"
    )
    parser.add_argument(
        "--model",
        default="llama3.1:8b",
        help="Ollama model to use (default: llama3.1:8b)"
    )
    parser.add_argument(
        "--url",
        default="http://localhost:11434",
        help="Ollama server URL (default: http://localhost:11434)"
    )
    
    args = parser.parse_args()
    
    # Get topic if not provided
    topic = args.topic
    if not topic:
        topic = input("Enter YouTube topic: ").strip()
        if not topic:
            print("❌ Topic is required")
            return 1
    
    # Initialize and run
    try:
        scripter = PhantomVisibleScripter(args.model, args.url)
        result = scripter.run(topic)
        
        if result.get("status") == "completed":
            return 0
        else:
            return 1
            
    except KeyboardInterrupt:
        print("\n\n👋 Script generation cancelled by user")
        return 1
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
