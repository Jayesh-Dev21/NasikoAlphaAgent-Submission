"""
Task planner for breaking down complex HR tasks.
"""
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
import json


class TaskPlanner:
    """Plans and breaks down complex tasks into subtasks."""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    def plan(self, query: str) -> List[Dict[str, Any]]:
        """Break down a query into actionable tasks."""
        
        prompt = f"""You are an HR task planner. Break down the following request into specific, actionable tasks.

Request: {query}

Return a JSON array of tasks. Each task should have:
- type: one of [schedule, recruit, research, interview_prep, culture_fit]
- description: what needs to be done
- priority: high, medium, or low
- params: relevant parameters for the task

Example:
[
  {{"type": "research", "description": "Research candidate background", "priority": "high", "params": {{"candidate_name": "John Doe"}}}},
  {{"type": "schedule", "description": "Schedule interview", "priority": "high", "params": {{"duration": 60, "type": "technical"}}}}
]

Return only the JSON array, no other text."""

        response = self.llm.invoke(prompt)
        
        try:
            tasks = json.loads(response.content)
            return tasks if isinstance(tasks, list) else []
        except json.JSONDecodeError:
            # Fallback: create a single generic task
            return [{
                "type": "general",
                "description": query,
                "priority": "medium",
                "params": {}
            }]
