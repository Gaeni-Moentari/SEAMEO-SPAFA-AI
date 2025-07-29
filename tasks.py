from crewai import Task
from agents import SEAMEOSPAFAAgents

class SEAMEOSPAFATasks:
    def __init__(self, agents: SEAMEOSPAFAAgents):
        self.agents = agents
    
    def create_research_task(self, user_question: str) -> Task:
        """Task for searching information from SEAMEO SPAFA website"""
        search_query = self.agents.get_seameo_search_query(user_question)
        
        return Task(
            description=f"""
            Search for relevant information to answer user question: "{user_question}"
            
            Steps:
            1. Use search tool with query: "{search_query}"
            2. Focus on results from seameo-spafa.org domain
            3. Collect the most relevant and accurate information
            4. Ensure information comes from official SEAMEO SPAFA sources
            5. If no relevant information is found, report honestly
            
            IMPORTANT: 
            - ONLY use information from official SEAMEO SPAFA website
            - Do not create information or use general knowledge outside SEAMEO SPAFA
            - Provide source URLs for each piece of information found
            """,
            agent=self.agents.create_research_agent(),
            expected_output="Collection of relevant information from official SEAMEO SPAFA website with clear source URLs"
        )
    
    def create_answer_task(self, user_question: str) -> Task:
        """Task for composing answers based on research results"""
        return Task(
            description=f"""
            Answer the question "{user_question}" with MAXIMUM 2-3 paragraphs ONLY.
            
            REQUIRED FORMAT:
            1. Direct answer (1-2 paragraphs max)  
            2. Source URLs from seameo-spafa.org (if available)
            
            STRICT RULES:
            - NO introductions like "Based on my research..." or "According to..."
            - Get straight to the point
            - If no information found: "Maaf, saya tidak dapat menemukan informasi tersebut di website SEAMEO SPAFA."
            - If not SEAMEO SPAFA related: "Maaf, saya hanya dapat membantu dengan informasi terkait SEAMEO SPAFA."
            - Include website URLs at the end if information is found
            """,
            agent=self.agents.create_answer_agent(),
            expected_output="Concise answer (2-3 paragraphs max) with source URLs"
        )
    
    def create_quality_check_task(self, user_question: str) -> Task:
        """Task for verifying answer quality"""
        return Task(
            description=f"""
            Quick quality check for answer to: "{user_question}"
            
            Check:
            1. Answer is 2-3 paragraphs max? 
            2. No unnecessary intro/verbose text?
            3. Contains source URLs if info found?
            4. Uses correct "Maaf..." response if no info?
            
            If OK: Approve answer
            If not OK: Request revision
            """,
            agent=self.agents.create_quality_agent(),
            expected_output="Quick approval or revision request"
        )