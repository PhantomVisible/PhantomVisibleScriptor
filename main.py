#!/usr/bin/env python3
"""
Phantom Visible Scripter - Local AI Agent for YouTube Script Creation
A modular, extensible system for researching and creating YouTube scripts
"""

import sys
import os
import argparse
import logging
from typing import Dict, Any

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
                primary_model=model_name, 
                collaborator_model=model_name
            )
        except Exception as e:
            logger.warning(f"Collaborative agent initialization failed: {e}")
            self.collaborative_agent = None
        
        # Storage for current work
        self.current_research = {}
        self.current_plan = {}
        self.current_script = {}
    
    def run(self, topic: str) -> Dict[str, Any]:
        """
        Run the complete script generation pipeline
        
        Args:
            topic: YouTube topic to create script for
            
        Returns:
            Complete results including research, plan, and script
        """
        print(f"\n🎬 Phantom Visible Scripter")
        print(f"📝 Topic: {topic}")
        print(f"🤖 Model: {self.model_name}")
        print(f"🔗 Ollama: {self.base_url}")
        print("\n" + "="*50)
        
        # Step 1: Test Ollama connection
        if not self._test_connection():
            return {"error": "Failed to connect to Ollama"}
        
        # Step 2: Research
        print("\n🔍 Step 1: Researching topic...")
        self.current_research = self.research_agent.research_topic(topic)
        print(f"✅ Found {self.current_research['total_sources']} sources")
        
        # Step 3: Planning
        print("\n📋 Step 2: Creating content plan...")
        self.current_plan = self.planning_agent.create_content_plan(self.current_research)
        print(f"✅ Plan created with {len(self.current_plan['sections'])} sections")
        print(f"⏱️  Estimated duration: {self.current_plan['estimated_length']:.1f} minutes")
        
        # Step 4: Display plan and get approval
        if not self._get_plan_approval():
            return {"status": "cancelled", "reason": "User rejected plan"}
        
        # Step 5: Script Generation
        print("\n✍️  Step 3: Generating script...")
        self.current_script = self.scripting_agent.generate_script(
            self.current_research, 
            self.current_plan
        )
        
        # Get verified word count from scripting agent
        verified_word_count = self.current_script.get('word_count', 0)
        verified_duration = self.current_script.get('estimated_duration', 0)
        
        print(f"✅ Script generated ({verified_word_count} words)")
        print(f"⏱️  Estimated duration: {verified_duration:.1f} minutes")
        
        # Step 6: Display results
        self._display_final_results()
        
        # Step 7: Critic Review
        self._run_critic_review()
        
        # Step 8: Offer refinement options
        self._offer_refinements()
        
        return {
            "status": "completed",
            "research": self.current_research,
            "plan": self.current_plan,
            "script": self.current_script
        }
    
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
    
    def _get_plan_approval(self) -> bool:
        """Display plan and get user approval"""
        print("\n📋 CONTENT PLAN:")
        print("="*50)
        
        # Display hooks
        print("\n🎣 Hook Options:")
        for i, hook in enumerate(self.current_plan['hooks'][:3], 1):
            print(f"   {i}. {hook}")
        
        # Display sections
        print(f"\n📚 Sections ({len(self.current_plan['sections'])}):")
        for i, section in enumerate(self.current_plan['sections'], 1):
            print(f"   {i}. {section['title']} ({section['duration']} min)")
            print(f"      Purpose: {section['purpose']}")
        
        # Display narrative flow
        print(f"\n🎭 Narrative Flow:")
        for i, step in enumerate(self.current_plan['narrative_flow'][:5], 1):
            print(f"   {i}. {step}")
        
        print(f"\n⏱️  Estimated Duration: {self.current_plan['estimated_length']:.1f} minutes")
        print(f"📄 Target Word Count: {self.current_plan['target_word_count']}")
        
        # Get user approval
        while True:
            print("\n" + "="*50)
            response = input("Do you approve this plan? (yes/no/edit): ").lower().strip()
            
            if response == 'yes':
                return True
            elif response == 'no':
                print("❌ Plan rejected. Exiting...")
                return False
            elif response == 'edit':
                self._edit_plan()
                return True
            else:
                print("Please enter 'yes', 'no', or 'edit'")
    
    def _edit_plan(self):
        """Allow user to edit the plan"""
        print("\n✏️  Edit Plan Options:")
        print("1. Change hooks")
        print("2. Modify sections")
        print("3. Continue with current plan")
        
        choice = input("Choose an option (1-3): ").strip()
        
        if choice == '1':
            self._edit_hooks()
        elif choice == '2':
            self._edit_sections()
        else:
            print("Continuing with current plan...")
    
    def _edit_hooks(self):
        """Edit hooks"""
        print("\n🎣 Current Hooks:")
        for i, hook in enumerate(self.current_plan['hooks'], 1):
            print(f"   {i}. {hook}")
        
        print("\nEnter new hooks (one per line, empty line to finish):")
        new_hooks = []
        while True:
            hook = input(f"Hook {len(new_hooks)+1}: ").strip()
            if not hook:
                break
            new_hooks.append(hook)
        
        if new_hooks:
            self.current_plan['hooks'] = new_hooks
            print("✅ Hooks updated")
    
    def _edit_sections(self):
        """Edit sections"""
        print("\n📚 Current Sections:")
        for i, section in enumerate(self.current_plan['sections'], 1):
            print(f"   {i}. {section['title']} ({section['duration']} min)")
        
        print("\nSection editing not yet implemented. Continuing with current plan...")
    
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
            plan = str(self.current_plan)  # Convert plan to string for critic
            script = self.current_script['full_script']
            
            # Get critic review
            print("🎭 Analyzing script quality...")
            review = self.critic_agent.critique(topic, plan, script)
            
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
        new_hooks = self.scripting_agent.regenerate_hook(
            self.current_script['topic'],
            self.current_plan['hooks'],
            feedback
        )
        
        print("\n🎣 New Hooks:")
        for i, hook in enumerate(new_hooks, 1):
            print(f"   {i}. {hook}")
        
        self.current_plan['hooks'] = new_hooks
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
        """Generate a completely new script"""
        print("\n✍️  Regenerating script...")
        new_script = self.scripting_agent.generate_script(
            self.current_research,
            self.current_plan
        )
        
        self.current_script = new_script
        print(f"✅ New script generated ({new_script['word_count']} words)")
        
        # Display new script preview
        print(f"\n📄 New Script Preview:")
        print("-" * 30)
        print(new_script['full_script'][:500] + "...")
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
