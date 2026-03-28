"""
Core HR agent logic with modular architecture.
"""
from typing import List, Dict, Any
import logging

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferMemory

# Import tools
from tools import (
    add_candidate_to_database,
    get_candidate_from_database,
    search_candidates_by_name,
    search_candidates_by_skills,
    search_candidates_advanced,
    schedule_interview,
    screen_candidate,
    research_candidate,
    get_interview_prep,
    analyze_culture_fit,
    research_salary,
    hr_assistant,
    set_modular_components
)

# Import modular architecture
from core.planner import TaskPlanner
from core.router import TaskRouter
from core.executor import Executor
from core.aggregator import ResultAggregator

# Import specialized modules
from modules.calendar_manager import CalendarManager
from modules.recruiter import Recruiter
from modules.researcher import Researcher
from modules.interview_coach import InterviewCoach
from modules.culture_analyzer import CultureAnalyzer

logger = logging.getLogger(__name__)

memory = ConversationBufferMemory(
    memory_key="chat_history",
    return_messages=True
)

class Agent:
    """HR Agent with modular architecture and LangChain integration."""
    
    def __init__(self):
        self.name = "HR Agent - Agents of Chaos"
        
        logger.info("Initializing HR Agent...")

        # Initialize modular architecture
        self.planner = TaskPlanner()
        self.router = TaskRouter()
        self.executor = Executor(self.router)
        self.aggregator = ResultAggregator()

        # Register specialized modules
        self._register_modules()

        # Set modular components for tools
        set_modular_components(self.planner, self.executor, self.aggregator)

        # Define tools (organized for clarity)
        self.tools = self._get_tools()

        # Initialize LLM with optimized settings
        self.llm = ChatOpenAI(
            model="gpt-4o",
            temperature=0.2,
            max_retries=2,
            request_timeout=30
        )

        # Create agent with prompt
        prompt = self._create_prompt()
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)

        # Create agent executor with optimized settings
        self.agent_executor = AgentExecutor(
            agent=agent,
            memory=memory,
            tools=self.tools,
            verbose=True,
            max_iterations=10,
            handle_parsing_errors=True
        )
        
        logger.info("✅ HR Agent initialized successfully")
    
    def _register_modules(self):
        """Register all specialized modules."""
        modules = [
            CalendarManager(),
            Recruiter(),
            Researcher(),
            InterviewCoach(),
            CultureAnalyzer()
        ]
        
        for module in modules:
            self.router.register_module(module)
            logger.info(f"Registered module: {module.__class__.__name__}")
    
    def _get_tools(self) -> List:
        """Get all available tools organized by category."""
        return [
            # Database tools
            add_candidate_to_database,
            get_candidate_from_database,
            search_candidates_by_name,
            search_candidates_by_skills,
            search_candidates_advanced,
            # HR workflow tools
            schedule_interview,
            screen_candidate,
            research_candidate,
            get_interview_prep,
            analyze_culture_fit,
            research_salary,
            # General assistant
            hr_assistant
        ]
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Create the system prompt for the agent."""
        return ChatPromptTemplate.from_messages([
            ("system",
             """You are an expert HR assistant.

Your role is to help with:
1. SCHEDULING: Schedule interviews and meetings
2. RECRUITING: Screen candidates, evaluate resumes, manage hiring pipeline
3. RESEARCH: Research candidates, companies, salaries, and market trends
4. INTERVIEW PREP: Generate interview questions according to job requirements and candidate background
5. CULTURE FIT: Analyze candidate-company alignment and team dynamics

Available tools:
- add_candidate_to_database: Add new candidates directly to MongoDB database
- get_candidate_from_database: Retrieve candidate info from MongoDB by email
- search_candidates_by_name: Search candidates by name (partial match, e.g., "Bob")
- search_candidates_by_skills: Find all candidates with specific skills (e.g., "Python, AWS")
- search_candidates_advanced: Advanced search by college, CPI, experience, status
- schedule_interview: Schedule interviews with candidates
- screen_candidate: Evaluate and screen candidates (auto-retrieves from database)
- research_candidate: Research candidate backgrounds
- get_interview_prep: Generate interview questions and prep materials
- analyze_culture_fit: Assess culture compatibility
- research_salary: Get salary data and compensation info
- hr_assistant: Handle complex multi-step HR tasks

DATABASE USAGE:
- When asked to add a candidate, use add_candidate_to_database directly
- When asked about a candidate by NAME (e.g., "tell me about Bob"), use search_candidates_by_name
- When asked for candidates with SKILLS (e.g., "who knows Python"), use search_candidates_by_skills
- When asked by email, use get_candidate_from_database
- For complex queries (college, CPI, experience), use search_candidates_advanced
- When asked to RESEARCH a candidate, ALWAYS use research_candidate tool directly - never ask for clarification
- When screening a candidate by email, screen_candidate will auto-retrieve from database

GUIDELINES:
- Be professional, helpful, concise, and efficient
- Use specific tools for focused tasks
- Use hr_assistant for complex multi-step requests
- Provide actionable insights and recommendations
- Consider both hard skills and culture fit in evaluations
- When scheduling interviews:
- If only the candidate name is provided, first check the database for the email.
- Do NOT ask the user for the email if the candidate exists in the database.

Always aim to provide comprehensive, practical assistance."""),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

    def process_message(self, message_text: str) -> str:
        """
        Process the incoming message using LangChain.
        
        Args:
            message_text: User's input message
            
        Returns:
            Agent's response text
        """
        try:
            result = self.agent_executor.invoke({"input": message_text})
            return result["output"]
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            return f"I apologize, but I encountered an error processing your request: {str(e)}. Please try again or rephrase your question."