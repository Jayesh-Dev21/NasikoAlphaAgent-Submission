"""
Planner - LLM-powered task decomposition

Unified Business Agent - Team Sleepyhead
Nasiko Hackathon 2026
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional

from langchain_groq import ChatGroq

logger = logging.getLogger(__name__)


class TaskPlanner:
    """
    Uses Groq LLM to break down complex queries into structured tasks.
    
    The planner analyzes user queries and creates a list of tasks that
    need to be executed sequentially to fulfill the user's request.
    """

    def __init__(self):
        """Initialize the Planner with Groq llama-3.1-70b model."""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")

        model = os.getenv("GROQ_MODEL_SECONDARY", "llama-3.1-70b-versatile")
        temperature = float(os.getenv("PLANNER_TEMPERATURE", "0.0"))

        self.llm = ChatGroq(
            groq_api_key=api_key,
            model_name=model,
            temperature=temperature,  # Deterministic planning
            max_retries=0,
            request_timeout=15,
        )

        logger.info(f"Planner initialized with model: {model}, temperature: {temperature}")

    def plan(self, query: str, context: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Break down a user query into structured tasks.
        
        Args:
            query: User's natural language query
            context: Optional context information
            
        Returns:
            List of task dictionaries, each with:
                - type: Task type (e.g., "create_ticket", "analyze_data")
                - description: Human-readable task description
                - priority: Task priority (high, medium, low)
                - params: Parameters needed for task execution
                
        Example output:
            [
                {
                    "type": "process_invoice",
                    "description": "Extract data from invoice PDF",
                    "priority": "high",
                    "params": {"file_path": "/uploads/invoice.pdf"}
                },
                {
                    "type": "create_expense",
                    "description": "Create expense record from invoice data",
                    "priority": "high",
                    "params": {"amount": 1250, "vendor": "Acme Corp"}
                }
            ]
        """
        prompt = self._build_planning_prompt(query, context)

        try:
            response = self.llm.invoke(prompt)
            response_text = response.content.strip()

            # Extract JSON from response (handle code blocks)
            tasks = self._parse_tasks(response_text)

            logger.info(f"Planned {len(tasks)} tasks for query: {query[:100]}...")
            return tasks

        except Exception as e:
            logger.error(f"Planning failed: {str(e)}")
            # Fallback: create a single generic task
            return [
                {
                    "type": "general_query",
                    "description": query,
                    "priority": "medium",
                    "params": {"query": query},
                }
            ]

    def _build_planning_prompt(self, query: str, context: Optional[Dict[str, Any]] = None) -> str:
        """Build the planning prompt for the LLM."""
        prompt = f"""You are a task planner for a business AI agent. Break down the user's query into specific, actionable tasks.

Available task types:
- create_ticket: Create a customer support ticket
- get_ticket: Retrieve ticket information
- update_ticket: Update ticket status
- analyze_sentiment: Analyze text sentiment
- load_dataset: Load data from file
- analyze_data: Perform data analysis
- generate_report: Create analytical reports
- add_expense: Add an expense record
- process_invoice: Extract data from invoice (OCR)
- get_expenses: Retrieve expense records
- financial_report: Generate financial summaries
- schedule_meeting: Create calendar event
- find_slots: Find available time slots
- extract_document: Extract text from document
- general_query: For simple questions or unknown tasks

User Query: {query}

"""

        if context:
            prompt += f"Context: {json.dumps(context, indent=2)}\n\n"

        prompt += """Output a JSON array of tasks. Each task should have:
- type: One of the task types above
- description: Clear description of what the task does
- priority: high, medium, or low
- params: Object with parameters needed (can be empty if unknown)

Return ONLY valid JSON, no explanations. Example:
[
  {
    "type": "create_ticket",
    "description": "Create support ticket for user",
    "priority": "high",
    "params": {"customer_email": "user@example.com", "subject": "Issue", "description": "Details"}
  }
]

JSON output:"""

        return prompt

    def _parse_tasks(self, response_text: str) -> List[Dict[str, Any]]:
        """
        Parse LLM response to extract task list.
        
        Handles responses that include code blocks, extra text, etc.
        """
        # Remove markdown code blocks if present
        if "```json" in response_text:
            start = response_text.find("```json") + 7
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()
        elif "```" in response_text:
            start = response_text.find("```") + 3
            end = response_text.find("```", start)
            response_text = response_text[start:end].strip()

        # Find JSON array
        start_idx = response_text.find("[")
        end_idx = response_text.rfind("]") + 1

        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON array found in response")

        json_str = response_text[start_idx:end_idx]

        try:
            tasks = json.loads(json_str)
            if not isinstance(tasks, list):
                raise ValueError("Response is not a JSON array")

            # Validate task structure
            for task in tasks:
                if "type" not in task:
                    task["type"] = "general_query"
                if "description" not in task:
                    task["description"] = "Task execution"
                if "priority" not in task:
                    task["priority"] = "medium"
                if "params" not in task:
                    task["params"] = {}

            return tasks

        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed: {str(e)}")
            logger.debug(f"Failed JSON: {json_str}")
            raise ValueError(f"Invalid JSON in response: {str(e)}")
