"""
Style Trainer for Phantom Visible Scripter
Fine-tunes models based on user's existing script style
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List
import sys

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from utils.ollama_client import OllamaClient

logger = logging.getLogger(__name__)

class StyleTrainer:
    """Train models to mimic user's script writing style"""
    
    def __init__(self, ollama_client: OllamaClient):
        self.ollama = ollama_client
        
    def create_style_prompt(self, training_data: Dict[str, Any]) -> str:
        """Create style analysis prompt from training data"""
        metadata = training_data.get("metadata", {})
        patterns = metadata.get("style_patterns", {})
        
        return f"""
You are a YouTube script writer who needs to adopt a specific writing style.

STYLE ANALYSIS:
- Total Scripts Analyzed: {metadata.get('total_scripts', 0)}
- Average Word Count: {metadata.get('avg_word_count', 0):.0f} words
- Common Hook Patterns: {', '.join(patterns.get('common_hooks', []))}
- Common Transitions: {', '.join(patterns.get('common_transitions', []))}
- Vocabulary Diversity: {patterns.get('avg_vocabulary_diversity', 0):.2f}

WRITING STYLE GUIDELINES:
1. Use these hook patterns: {', '.join(patterns.get('common_hooks', [])[:3])}
2. Use these transitions: {', '.join(patterns.get('common_transitions', [])[:3])}
3. Maintain conversational tone with questions
4. Target word count: {metadata.get('avg_word_count', 1500):.0f} words
5. Keep vocabulary accessible but varied

EXAMPLE SCRIPT EXCERPT:
{self._get_example_excerpt(training_data)}

Your task is to write a new YouTube script following this exact style.
"""
    
    def _get_example_excerpt(self, training_data: Dict[str, Any]) -> str:
        """Get example excerpt from training data"""
        scripts = training_data.get("scripts", [])
        if not scripts:
            return "No examples available"
        
        # Get first script as example
        first_script = scripts[0]
        content = first_script.get("content", "")
        
        # Return first 200 characters as example
        return content[:200] + "..." if len(content) > 200 else content
    
    def generate_style_guide(self, training_data_file: str = "training_data/style_dataset.json") -> str:
        """Generate comprehensive style guide from training data"""
        try:
            with open(training_data_file, 'r', encoding='utf-8') as f:
                training_data = json.load(f)
            
            style_prompt = self.create_style_prompt(training_data)
            
            # Save style guide
            style_guide_path = Path("training_data/style_guide.txt")
            style_guide_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(style_guide_path, 'w', encoding='utf-8') as f:
                f.write(style_prompt)
            
            logger.info(f"Style guide saved to: {style_guide_path}")
            return style_prompt
            
        except Exception as e:
            logger.error(f"Failed to generate style guide: {e}")
            return f"Error: {e}"
    
    def test_style_generation(self, topic: str, style_guide_file: str = "training_data/style_guide.txt") -> str:
        """Test script generation using trained style"""
        try:
            # Load style guide
            with open(style_guide_file, 'r', encoding='utf-8') as f:
                style_prompt = f.read()
            
            # Generate script using style
            system_prompt = "You are a YouTube script writer who perfectly mimics the user's established writing style."
            prompt = f"""
Write a YouTube script about "{topic}" following this exact style:

{style_prompt}

Write the opening hook only (first 2-3 sentences).
"""
            
            response = self.ollama.generate_response(prompt, system_prompt)
            return response
            
        except Exception as e:
            logger.error(f"Style test failed: {e}")
            return f"Error: {e}"

def main():
    """Main function to demonstrate style training"""
    print("🎯 Phantom Visible Scripter - Style Trainer")
    print("=" * 50)
    
    # Check if training data exists
    training_file = Path("training_data/style_dataset.json")
    if not training_file.exists():
        print("❌ Training data not found!")
        print("📁 First run: python training_data_processor.py")
        print("💡 Then run: python style_trainer.py")
        return
    
    # Initialize trainer
    from utils.ollama_client import OllamaClient
    ollama = OllamaClient()
    trainer = StyleTrainer(ollama)
    
    # Generate style guide
    print("\n📚 Creating style guide from your scripts...")
    style_guide = trainer.generate_style_guide()
    
    if style_guide and not style_guide.startswith("Error"):
        print("✅ Style guide created successfully!")
        
        # Test style generation
        print("\n🧪 Testing style generation...")
        topic = input("Enter a test topic: ").strip()
        
        if topic:
            test_script = trainer.test_style_generation(topic)
            print(f"\n📝 Generated script excerpt:\n{test_script}")
    
    print("\n🚀 Integration complete!")
    print("📋 Next steps:")
    print("1. Update ScriptingAgent to use your style guide")
    print("2. Modify prompts/scripting_prompt.txt to include style instructions")
    print("3. Run: python main.py 'your topic'")

if __name__ == "__main__":
    main()
