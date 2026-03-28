"""
Result aggregator for combining outputs from multiple modules.
"""
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI


class ResultAggregator:
    """Aggregates and summarizes results from multiple tasks."""
    
    def __init__(self):
        self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.3)
    
    def combine(self, results: List[Dict[str, Any]]) -> str:
        """Combine multiple task results into a coherent response."""
        
        if not results:
            return "No results to aggregate."
        
        # Format results for the LLM
        formatted_results = []
        for i, result in enumerate(results, 1):
            task_desc = result.get("task", {}).get("description", "Unknown task")
            status = result.get("status", "unknown")
            module = result.get("module", "unknown")
            result_data = result.get("result", {})
            
            formatted_results.append(
                f"Task {i}: {task_desc}\n"
                f"Module: {module}\n"
                f"Status: {status}\n"
                f"Result: {result_data}\n"
            )
        
        results_text = "\n".join(formatted_results)
        
        prompt = f"""You are an HR assistant. Multiple tasks have been completed. 
Synthesize the following results into a clear, professional, and helpful response for the user.

Results:
{results_text}

Provide a natural, conversational summary that:
1. Highlights key information
2. Mentions any actions taken
3. Provides next steps if applicable
4. Is concise but complete

Response:"""

        response = self.llm.invoke(prompt)
        return response.content
