import os
from dotenv import load_dotenv
from crewai import Crew, Process
from agents import SEAMEOSPAFAAgents
from tasks import SEAMEOSPAFATasks
import streamlit as st

# Load environment variables
load_dotenv()

class SEAMEOSPAFACrewManager:
    def __init__(self):
        self.agents = SEAMEOSPAFAAgents()
        self.tasks = SEAMEOSPAFATasks(self.agents)
    
    def process_question(self, user_question: str) -> dict:
        """
        Process user question through CrewAI workflow
        Returns: dict with answer and metadata
        """
        try:
            # Create tasks
            research_task = self.tasks.create_research_task(user_question)
            answer_task = self.tasks.create_answer_task(user_question) 
            quality_task = self.tasks.create_quality_check_task(user_question)
            
            # Create crew
            crew = Crew(
                agents=[
                    self.agents.create_research_agent(),
                    self.agents.create_answer_agent(),
                    self.agents.create_quality_agent()
                ],
                tasks=[research_task, answer_task, quality_task],
                process=Process.sequential,
                verbose=True
            )
            
            # Execute crew
            with st.spinner("🔍 Searching information from SEAMEO SPAFA website..."):
                result = crew.kickoff()
            
            # Extract the answer from the answer task, not the quality check
            answer_output = answer_task.output.raw if hasattr(answer_task, 'output') and answer_task.output else str(result)
            
            return {
                "success": True,
                "answer": answer_output,
                "question": user_question,
                "status": "completed"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "question": user_question,
                "status": "error"
            }
    
    def validate_question(self, question: str) -> dict:
        """
        Basic validation for user questions
        """
        if not question or len(question.strip()) < 5:
            return {
                "valid": False,
                "message": "Question is too short. Please ask a more specific question."
            }
        
        if len(question) > 500:
            return {
                "valid": False,
                "message": "Question is too long. Please make a more concise question (maximum 500 characters)."
            }
        
        return {
            "valid": True,
            "message": "Question is valid"
        }

# Singleton instance
crew_manager = SEAMEOSPAFACrewManager()