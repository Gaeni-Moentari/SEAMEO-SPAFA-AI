import os
from crewai import Agent
from crewai_tools import SerperDevTool
from langchain_openai import ChatOpenAI
import json
from typing import List

class SEAMEOSPAFAAgents:
    def __init__(self):
        self.llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o"),
            temperature=float(os.getenv("TEMPERATURE", "0.1")),
            max_tokens=int(os.getenv("MAX_TOKENS", "2000"))
        )
        
        # Load SEAMEO SPAFA URLs
        with open('seameo_urls.json', 'r') as f:
            self.urls_config = json.load(f)
        
        # Initialize search tool with domain restriction
        self.search_tool = SerperDevTool(
            search_url="https://google.serper.dev/search",
            n_results=5
        )
    
    def create_research_agent(self) -> Agent:
        """Agent for searching information from SEAMEO SPAFA website"""
        return Agent(
            role="SEAMEO SPAFA Information Researcher",
            goal="Search for accurate and relevant information from official SEAMEO SPAFA website to answer user questions",
            backstory="""
            You are a specialized information researcher for SEAMEO SPAFA (Southeast Asian Ministers of Education Organization - 
            Regional Centre for Archaeology and Fine Arts). You have access to the official SEAMEO SPAFA website and 
            are responsible for finding accurate information to help users understand the organization, programs, 
            research, and services provided by SEAMEO SPAFA.
            
            IMPORTANT: You may ONLY use information from seameo-spafa.org domain and related official sources.
            Do not provide information that is not sourced from the official SEAMEO SPAFA website.
            """,
            tools=[self.search_tool],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def create_answer_agent(self) -> Agent:
        """Agent for composing answers based on research results"""
        return Agent(
            role="SEAMEO SPAFA Help Center Assistant",
            goal="Provide concise, direct answers (2-3 paragraphs) based on official SEAMEO SPAFA information",
            backstory="""
            You are a virtual assistant for SEAMEO SPAFA Help Center. Provide CONCISE and DIRECT answers.
            
            ANSWER FORMAT REQUIREMENTS:
            - Maximum 2-3 paragraphs only
            - Get straight to the point
            - No lengthy introductions or explanations
            - Include source URLs from seameo-spafa.org at the end
            - If no information found, simply say "Maaf, saya tidak dapat menemukan informasi tersebut di website SEAMEO SPAFA"
            
            STRICT RULES:
            - NO verbose or lengthy responses
            - Answer ONLY what is asked
            - Use English language
            - ONLY answer SEAMEO SPAFA related questions
            """,
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def create_quality_agent(self) -> Agent:
        """Agent for verifying answer quality and accuracy"""
        return Agent(
            role="Quality Assurance Specialist",
            goal="Ensure answers are concise (2-3 paragraphs max) and include source URLs",
            backstory="""
            You verify that answers are:
            1. Maximum 2-3 paragraphs
            2. Direct and to the point
            3. Include source URLs when information is found
            4. Use "Maaf..." responses when no information available
            
            Approve concise answers or request revision for verbose ones.
            """,
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
    
    def get_seameo_search_query(self, user_question: str) -> str:
        """Generate search query with SEAMEO SPAFA domain restriction"""
        domains = " OR ".join([f"site:{domain}" for domain in self.urls_config["search_domains"]])
        return f"({domains}) {user_question}"