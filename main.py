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
        Initialize the Phantom Visible Scripter
        
        Args:
            model_name: Ollama model to use
            base_url: Ollama server URL
        """
        self.model_name = model_name
        self.base_url = base_url
        
        # Initialize Ollama client
        self.ollama = OllamaClient(model_name, base_url)
        
        # Initialize agents
        self.research_agent = ResearchAgent(self.ollama)
        self.planning_agent = PlanningAgent(self.ollama)
        self.scripting_agent = ScriptingAgent(self.ollama)
        self.critic_agent = CriticAgent(self.ollama)
        
        # Store current work
        self.current_research = None
        self.current_plan = None
        self.current_script = None
    
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
        print(f"✅ Script generated ({self.current_script['word_count']} words)")
        print(f"⏱️  Estimated duration: {self.current_script['estimated_duration']:.1f} minutes")
        
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
        
        print(f"\n📝 Topic: {self.current_script['topic']}")
        print(f"📊 Word Count: {self.current_script['word_count']}")
        print(f"⏱️  Duration: {self.current_script['estimated_duration']:.1f} minutes")
        
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
            print("5. Exit")
            
            choice = input("Choose an option (1-5): ").strip()
            
            if choice == '1':
                self._regenerate_hooks()
            elif choice == '2':
                self._refine_section()
            elif choice == '3':
                self._regenerate_script()
            elif choice == '4':
                self._save_script()
            elif choice == '5':
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
    
    def _save_script(self):
        """Save script to file"""
        filename = input("Enter filename (without extension): ").strip()
        if not filename:
            filename = f"script_{self.current_script['topic'].replace(' ', '_')}"
        
        filepath = f"{filename}.txt"
        
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(f"Phantom Visible Scripter - YouTube Script\n")
                f.write(f"Topic: {self.current_script['topic']}\n")
                f.write(f"Word Count: {self.current_script['word_count']}\n")
                f.write(f"Estimated Duration: {self.current_script['estimated_duration']:.1f} minutes\n")
                f.write(f"Generated: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write("\n" + "="*50 + "\n\n")
                
                f.write("TALKING POINTS:\n")
                for i, point in enumerate(self.current_script['talking_points'], 1):
                    f.write(f"{i}. {point}\n")
                f.write("\n" + "-"*50 + "\n\n")
                
                f.write("FULL SCRIPT:\n")
                f.write(self.current_script['full_script'])
            
            print(f"✅ Script saved to {filepath}")
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
