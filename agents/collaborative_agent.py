"""
Collaborative Agent for Phantom Visible Scripter
Handles multi-model collaboration for script improvement and discussion
"""

import logging
from typing import Dict, List, Any
from utils.ollama_client import OllamaClient

logger = logging.getLogger(__name__)

class CollaborativeAgent:
    """Agent for managing multi-model collaboration and script improvement"""
    
    def __init__(self, primary_model: str = "llama3.1:8b", collaborator_model: str = "llama3.1:8b"):
        """
        Initialize Collaborative Agent
        
        Args:
            primary_model: Model that generated the original script
            collaborator_model: Model that will review and improve the script
        """
        self.primary_model = primary_model
        self.collaborator_model = collaborator_model
        self.primary_client = OllamaClient(model_name=primary_model)
        self.collaborator_client = OllamaClient(model_name=collaborator_model)
        
    def collaborative_review(self, script: str, original_topic: str, user_feedback: str = "") -> Dict[str, Any]:
        """
        Have two models discuss and improve the script
        
        Args:
            script: Original script to review
            original_topic: The original topic for context
            user_feedback: Specific user feedback or concerns
            
        Returns:
            Collaborative review results
        """
        logger.info(f"Starting collaborative review with models: {self.primary_model} + {self.collaborator_model}")
        
        # Step 1: Primary model analyzes its own work
        primary_analysis = self._get_self_analysis(script, original_topic)
        
        # Step 2: Collaborator model reviews the script
        collaborator_review = self._get_collaborator_review(script, original_topic, primary_analysis, user_feedback)
        
        # Step 3: Models discuss and reach consensus
        consensus = self._facilitate_discussion(primary_analysis, collaborator_review, user_feedback)
        
        return {
            "primary_analysis": primary_analysis,
            "collaborator_review": collaborator_review,
            "consensus": consensus,
            "models_used": [self.primary_model, self.collaborator_model],
            "improvement_suggestions": consensus.get('suggestions', []),
            "final_recommendations": consensus.get('recommendations', [])
        }
    
    def _get_self_analysis(self, script: str, topic: str) -> Dict[str, Any]:
        """Primary model analyzes its own script"""
        system_prompt = """You are the original author of a YouTube script. Analyze your own work honestly and identify areas for improvement.
Be self-critical but constructive. Focus on what could be better, not what's wrong."""
        
        prompt = f"""
You wrote this YouTube script about "{topic}". Please analyze it honestly:

{script}

Provide analysis covering:
1. **Strengths**: What worked well in your script
2. **Weaknesses**: What could be improved 
3. **Content Gaps**: What's missing or underdeveloped
4. **Engagement Issues**: Where might viewers lose interest
5. **Structure Problems**: Flow and organization issues
6. **Word Count**: Is the length appropriate for the topic?
7. **Self-Critique**: What would you do differently next time?

Be specific and constructive. This will help another AI model improve your work.
"""
        
        try:
            response = self.primary_client.generate_response(prompt, system_prompt)
            return {"analysis": response, "model": self.primary_model}
        except Exception as e:
            logger.error(f"Primary model analysis failed: {e}")
            return {"analysis": "Failed to analyze", "model": self.primary_model}
    
    def _get_collaborator_review(self, script: str, topic: str, primary_analysis: Dict, user_feedback: str) -> Dict[str, Any]:
        """Collaborator model reviews the script and primary analysis"""
        system_prompt = """You are a collaborative script editor reviewing another AI's work.
Be constructive, specific, and focus on making the script better.
Consider both the original script and the primary model's self-analysis."""
        
        context = f"""
Original Topic: {topic}

Primary Model ({primary_analysis.get('model', 'Unknown')}) Self-Analysis:
{primary_analysis.get('analysis', 'Not available')}

User Feedback: {user_feedback if user_feedback else 'No specific feedback provided'}

Script to Review:
{script}

Please provide detailed review covering:
1. **Agreement**: What do you agree with from the primary analysis?
2. **Disagreement**: What do you see differently?
3. **Improvement Ideas**: Specific suggestions to enhance the script
4. **Content Additions**: What's missing that should be added?
5. **Structure Changes**: How to improve flow and organization
6. **Engagement Boosters**: Ideas to make it more compelling
7. **Technical Issues**: Word count, pacing, clarity problems

Focus on actionable, specific improvements that will make this script exceptional.
"""
        
        try:
            response = self.collaborator_client.generate_response(context, system_prompt)
            return {"review": response, "model": self.collaborator_model}
        except Exception as e:
            logger.error(f"Collaborator review failed: {e}")
            return {"review": "Failed to review", "model": self.collaborator_model}
    
    def _facilitate_discussion(self, primary_analysis: Dict, collaborator_review: Dict, user_feedback: str) -> Dict[str, Any]:
        """Facilitate discussion between models to reach consensus"""
        system_prompt = """You are a facilitator mediating between two AI models.
Your goal is to synthesize their analyses and create actionable improvement recommendations.
Be balanced, practical, and focus on the best ideas from both models."""
        
        context = f"""
Primary Model Analysis ({primary_analysis.get('model', 'Unknown')}):
{primary_analysis.get('analysis', 'Not available')}

Collaborator Review ({collaborator_review.get('model', 'Unknown')}):
{collaborator_review.get('review', 'Not available')}

User Feedback: {user_feedback if user_feedback else 'No specific feedback provided'}

TASK: Create consensus recommendations for improving this script.

Please provide:
1. **Consensus Strengths**: What both models agree works well
2. **Priority Improvements**: Top 3-5 most important changes needed
3. **Content Enhancements**: Specific additions to make script better
4. **Structural Fixes**: How to improve organization and flow
5. **Engagement Strategies**: Ideas to increase viewer interest
6. **Technical Adjustments**: Word count, pacing, clarity improvements
7. **Next Steps**: Action plan for implementing improvements

Focus on practical, actionable steps that will result in a significantly improved script.
"""
        
        try:
            # Use primary model for final synthesis to maintain consistency
            response = self.primary_client.generate_response(context, system_prompt)
            return {"consensus": response, "facilitator": self.primary_model}
        except Exception as e:
            logger.error(f"Consensus facilitation failed: {e}")
            return {"consensus": "Failed to reach consensus", "facilitator": self.primary_model}
    
    def generate_improved_script(self, original_script: str, consensus_recommendations: Dict) -> str:
        """Generate improved version of script based on consensus recommendations"""
        system_prompt = """You are implementing improvements to a YouTube script.
Follow the consensus recommendations precisely to create an enhanced version.
Make the script substantially better while maintaining the original voice and style."""
        
        prompt = f"""
Original Script:
{original_script}

Consensus Recommendations:
{consensus_recommendations.get('consensus', 'No recommendations available')}

TASK: Create an improved version of this script incorporating all recommendations.

Requirements:
1. Implement all structural fixes suggested
2. Add all content enhancements recommended
3. Apply all engagement strategies
4. Address all technical issues
5. Maintain original tone and style
6. Ensure proper word count for the topic
7. Make it flow naturally and engaging

Write the complete improved script:
"""
        
        try:
            response = self.primary_client.generate_response(prompt, system_prompt)
            return response
        except Exception as e:
            logger.error(f"Script improvement failed: {e}")
            return "Failed to improve script"
    
    def get_improvement_summary(self, collaborative_result: Dict[str, Any]) -> str:
        """Generate summary of collaborative improvements"""
        improvements = collaborative_result.get('improvement_suggestions', [])
        recommendations = collaborative_result.get('final_recommendations', [])
        
        summary = f"""
🤝 COLLABORATIVE IMPROVEMENT SUMMARY
==========================================

Models Involved: {', '.join(collaborative_result.get('models_used', []))}

Key Improvements Identified:
{chr(10).join([f"• {imp}" for imp in improvements[:5]])}

Final Recommendations:
{chr(10).join([f"• {rec}" for rec in recommendations[:5]])}

Next Steps:
1. Review all improvement suggestions
2. Implement structural changes first
3. Add content enhancements
4. Test engagement improvements
5. Generate final version

This collaborative process ensures multiple perspectives lead to better scripts!
"""
        
        return summary
