"""
Core Agent with dual architecture (LangChain + Modular Pipeline).

Unified Business Agent - Team Sleepyhead
Nasiko Hackathon 2026
"""

import os
import logging
from typing import Dict, Any, Optional

from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain.memory import ConversationBufferMemory

# Import modular architecture components
from src.core.planner import TaskPlanner
from src.core.router import TaskRouter
from src.core.executor import TaskExecutor
from src.core.aggregator import ResultAggregator

# Import database
from src.utils.database import get_database

logger = logging.getLogger(__name__)


class Agent:
    """
    Unified Business Agent with dual architecture:
    
    1. LangChain Layer: Natural language understanding, tool selection, memory
    2. Modular Pipeline: Complex multi-step workflows (Planner → Router → Executor → Aggregator)
    
    The agent handles:
    - Customer Service (tickets, sentiment, FAQ)
    - Data Analytics (CSV/Excel analysis, reports, insights)
    - Finance/Accounting (expenses, invoices, budgets)
    - Scheduling (Google Calendar integration)
    - Document Processing (OCR, invoice parsing)
    """
    
    def __init__(self):
        """Initialize the agent with all components."""
        
        self.name = "Unified Business Agent - Team Sleepyhead"
        logger.info("=" * 80)
        logger.info("Initializing Unified Business Agent...")
        logger.info("=" * 80)
        
        # Initialize database
        self._init_database()
        
        # Initialize modular pipeline
        self._init_modular_pipeline()
        
        # Register modules
        self._register_modules()
        
        # Initialize LangChain layer
        self._init_langchain()
        
        logger.info("✅ Unified Business Agent initialized successfully")
        logger.info("=" * 80)
    
    def _init_database(self):
        """Initialize database connection."""
        try:
            self.db = get_database()
            logger.info(f"✅ Database initialized: {type(self.db).__name__}")
        except Exception as e:
            logger.error(f"❌ Database initialization failed: {e}")
            raise
    
    def _init_modular_pipeline(self):
        """Initialize the modular pipeline components."""
        logger.info("Initializing modular pipeline...")
        
        # Core pipeline components
        self.planner = TaskPlanner()
        logger.info("  ✓ Planner initialized")
        
        self.router = TaskRouter()
        logger.info("  ✓ Router initialized")
        
        self.executor = TaskExecutor(self.router)
        logger.info("  ✓ Executor initialized")
        
        self.aggregator = ResultAggregator()
        logger.info("  ✓ Aggregator initialized")
        
        logger.info("✅ Modular pipeline ready")
    
    def _register_modules(self):
        """Register all specialized modules with the router."""
        logger.info("Registering specialized modules...")
        
        # Import modules (these will be implemented next)
        try:
            from src.modules.customer_service import CustomerServiceModule
            from src.modules.data_analytics import DataAnalyticsModule
            from src.modules.finance import FinanceModule
            from src.modules.scheduling import SchedulingModule
            from src.modules.document_processor import DocumentProcessorModule
            
            modules = [
                CustomerServiceModule(self.db),
                DataAnalyticsModule(self.db),
                FinanceModule(self.db),
                SchedulingModule(self.db),
                DocumentProcessorModule(self.db),
            ]
            
            for module in modules:
                self.router.register_module(module)
                logger.info(f"  ✓ Registered: {module.__class__.__name__}")
            
            logger.info("✅ All modules registered")
            
        except ImportError as e:
            logger.warning(f"⚠️  Modules not yet implemented: {e}")
            logger.warning("⚠️  Agent will run with limited capabilities")
    
    def _init_langchain(self):
        """Initialize LangChain components (LLM, tools, agent, memory)."""
        logger.info("Initializing LangChain layer...")
        
        # 1. Memory (conversation history)
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
        logger.info("  ✓ Memory initialized")
        
        # 2. Tools (will be implemented in tools.py)
        self.tools = self._get_tools()
        logger.info(f"  ✓ {len(self.tools)} tools loaded")
        
        # 3. LLM (Groq with llama-3.3-70b-versatile)
        groq_api_key = os.getenv("GROQ_API_KEY")
        if not groq_api_key:
            logger.warning("⚠️  GROQ_API_KEY not set - using placeholder")
            groq_api_key = "placeholder"
        
        self.llm = ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.2,  # Balanced: professional but not robotic
            groq_api_key=groq_api_key,
            max_retries=0,
            request_timeout=20,
        )
        logger.info("  ✓ LLM initialized (Groq llama-3.3-70b-versatile, temp=0.2)")
        
        # 4. Prompt
        prompt = self._create_prompt()
        logger.info("  ✓ System prompt created")
        
        # 5. Agent
        agent = create_tool_calling_agent(self.llm, self.tools, prompt)
        logger.info("  ✓ Agent created")
        
        # 6. Agent Executor
        self.agent_executor = AgentExecutor(
            agent=agent,
            memory=self.memory,
            tools=self.tools,
            verbose=False,
            max_iterations=15,  # Allow complex multi-step tasks
            handle_parsing_errors=True,
            return_intermediate_steps=False
        )
        logger.info("  ✓ Agent Executor ready")
        
        logger.info("✅ LangChain layer initialized")
    
    def _get_tools(self):
        """
        Get all available tools.
        
        Tools will be implemented in tools.py and include:
        - Database tools (tickets, datasets, expenses, events, documents)
        - Customer service tools (sentiment analysis, FAQ)
        - Data analytics tools (load dataset, analyze, report)
        - Finance tools (add expense, invoice OCR, budget check)
        - Scheduling tools (schedule meeting, find slots)
        - Document tools (OCR, extract text)
        - Multi-step workflow tool (delegates to modular pipeline)
        """
        try:
            from src.tools import (
                # Will import tools when implemented
                get_all_tools,
                set_modular_components
            )
            
            # Set modular components for tools to use
            set_modular_components(
                planner=self.planner,
                executor=self.executor,
                aggregator=self.aggregator,
                database=self.db
            )
            
            return get_all_tools()
            
        except ImportError as e:
            logger.warning(f"⚠️  Tools not yet implemented: {e}")
            return []  # Empty tools for now
    
    def _create_prompt(self) -> ChatPromptTemplate:
        """Create the system prompt for the agent."""
        
        system_message = """You are a Unified Business Agent - a sophisticated AI assistant that handles multiple business domains with expertise and professionalism.

**YOUR CAPABILITIES:**

1. **CUSTOMER SERVICE**
   - Create, track, and resolve support tickets
   - Analyze customer sentiment (positive/negative/neutral)
   - Search FAQ knowledge base for quick answers
   - Send email notifications to customers

2. **DATA ANALYTICS**
   - Load and analyze datasets (CSV, Excel, JSON)
   - Generate statistical reports and insights
   - Detect patterns and trends in data
   - Query data with natural language
   - Visualize data findings

3. **FINANCE & ACCOUNTING**
   - Track expenses and categorize transactions
   - Process invoices with OCR (extract amounts, vendors, dates)
   - Check budgets and spending limits
   - Generate financial reports and summaries

4. **SCHEDULING & CALENDAR**
   - Schedule meetings with Google Calendar integration
   - Find available time slots for participants
   - Create events with Google Meet links
   - Send calendar invitations via email

5. **DOCUMENT PROCESSING**
   - Extract text from images and PDFs using OCR
   - Parse invoices and receipts automatically
   - Validate document formats and content
   - Process documents in batches

**AVAILABLE TOOLS:**

Database Tools:
- create_ticket, get_ticket, update_ticket, close_ticket
- load_dataset, get_dataset
- add_expense, get_expenses
- create_event, get_events
- save_document, get_documents

Domain-Specific Tools:
- analyze_sentiment, search_faq (Customer Service)
- analyze_dataset, generate_report, query_data (Analytics)
- process_invoice, check_budget, generate_financial_report (Finance)
- schedule_meeting, find_available_slots (Scheduling)
- extract_text_from_document, process_invoice_ocr (Documents)

Multi-Step Workflow:
- handle_complex_task: Automatically breaks down complex requests into steps using the modular pipeline (Planner → Router → Executor → Aggregator)

**GUIDELINES:**

1. **Be Professional**: Use clear, concise language. Avoid jargon unless necessary.

2. **Be Proactive**: 
   - Anticipate user needs
   - Suggest next steps
   - Provide actionable insights

3. **Tool Selection**:
   - Use specific tools for focused tasks
   - Use handle_complex_task for multi-step workflows
   - Combine tools when needed for comprehensive solutions

4. **Data Handling**:
   - Always validate inputs before processing
   - Handle errors gracefully with helpful messages
   - Protect sensitive information (PII, financial data)

5. **Response Style**:
   - Start with a brief acknowledgment
   - Provide clear status updates
   - Summarize results concisely
   - Offer follow-up options when relevant

6. **Domain Expertise**:
   - Customer Service: Empathetic, solution-oriented
   - Analytics: Data-driven, insightful
   - Finance: Precise, compliant
   - Scheduling: Efficient, respectful of time
   - Documents: Accurate, thorough

**EXAMPLES:**

User: "Create a support ticket for John Doe complaining about slow response times"
You: *Use create_ticket tool* → "I've created ticket #12345 for John Doe regarding slow response times. The ticket is marked as high priority. Would you like me to analyze the sentiment or send a notification?"

User: "Analyze the sales data from Q1 and tell me the trends"
You: *Use load_dataset → analyze_dataset → generate_report* → "Based on Q1 sales data: Revenue increased 23% MoM, top category was Electronics ($450K), peak sales occurred in March. I can create a detailed report if needed."

User: "Process this invoice and check if we're over budget"
You: *Use process_invoice_ocr → add_expense → check_budget* → "Invoice processed: $2,450 from Acme Corp for office supplies. This brings monthly spending to $18,200 / $20,000 budget (91%). You have $1,800 remaining."

Always strive to provide maximum value while maintaining accuracy and professionalism."""

        return ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history", optional=True),
            ("user", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

    def _capabilities_summary(self) -> str:
        """Return a fast, static capabilities response."""
        return (
            "I can help across five business areas: "
            "(1) customer support tickets and sentiment analysis, "
            "(2) data analytics for CSV/Excel/JSON datasets, "
            "(3) finance tasks like expenses, invoice OCR, and budget checks, "
            "(4) scheduling meetings and finding time slots, and "
            "(5) document OCR and extraction. "
            "You can ask me for single tasks or end-to-end multi-step workflows."
        )

    def _is_capability_query(self, text: str) -> bool:
        """Detect simple capability/help prompts that should skip LLM."""
        normalized = text.strip().lower()
        direct = {
            "what can you help me with?",
            "what can you help me with",
            "help",
            "capabilities",
            "what can you do",
            "what can you do?",
            "who are you",
            "who are you?",
        }
        if normalized in direct:
            return True
        return (
            "what can you" in normalized
            or "how can you" in normalized
            or "help me" in normalized
            or "capabilit" in normalized
        )
    
    def process_message(
        self,
        input_text: str,
        session_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Process a user message and return the agent's response.
        
        This is the main entry point called by the FastAPI server.
        
        Args:
            input_text: User's message text
            session_id: Optional session ID for conversation tracking
            context: Optional additional context
        
        Returns:
            Agent's response text
        """
        try:
            logger.info(f"Processing message (session: {session_id})")
            logger.debug(f"Input: {input_text}")

            # Fast-path for capability/help requests so the system remains responsive
            # even if external LLM calls are slow/unavailable.
            if self._is_capability_query(input_text):
                return self._capabilities_summary()
            
            # Invoke the agent executor
            result = self.agent_executor.invoke({
                "input": input_text,
                # Can add context here if needed
            })
            
            response_text = result["output"]
            logger.info(f"Response generated ({len(response_text)} chars)")
            logger.debug(f"Output: {response_text[:200]}...")
            
            return response_text
            
        except Exception as e:
            logger.error(f"Error processing message: {e}", exc_info=True)
            # If provider/network fails and this is a help-capability prompt,
            # return local static response instead of error text.
            if self._is_capability_query(input_text):
                return self._capabilities_summary()
            return (
                f"I apologize, but I encountered an error processing your request: {str(e)}. "
                "Please try again or rephrase your question. If the issue persists, "
                "contact support for assistance."
            )
