"""
Result Aggregator - Synthesizes multiple task results into coherent response

Unified Business Agent - Team Sleepyhead
Nasiko Hackathon 2026
"""

import logging
import os
from typing import List

from langchain_groq import ChatGroq

logger = logging.getLogger(__name__)


class ResultAggregator:
    """
    Aggregates multiple task results into a coherent, natural response.
    
    Uses Groq LLM to synthesize results from multiple modules into
    a professional, conversational response for the user.
    """

    def __init__(self):
        """Initialize the Aggregator with Groq llama-3.1-70b model."""
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable not set")

        model = os.getenv("GROQ_MODEL_SECONDARY", "llama-3.1-70b-versatile")
        temperature = float(os.getenv("AGGREGATOR_TEMPERATURE", "0.3"))

        self.llm = ChatGroq(
            groq_api_key=api_key,
            model_name=model,
            temperature=temperature,  # Natural but consistent
            max_retries=0,
            request_timeout=15,
        )

        logger.info(f"Aggregator initialized with model: {model}, temperature: {temperature}")

    def aggregate(self, results: List[str], original_query: str = "") -> str:
        """
        Aggregate multiple task results into a coherent response.
        
        Args:
            results: List of result strings from task executions
            original_query: Original user query for context
            
        Returns:
            str: Natural language summary of all results
        """
        if not results:
            return "No results to aggregate."

        # If only one result, might not need LLM synthesis
        if len(results) == 1:
            result = results[0]
            # If it's already well-formatted, return as-is
            if not result.startswith("✓") and not result.startswith("❌"):
                return result
            # Otherwise, clean it up
            return self._clean_single_result(result)

        # Multiple results: use LLM to synthesize
        prompt = self._build_aggregation_prompt(results, original_query)

        try:
            response = self.llm.invoke(prompt)
            aggregated_text = response.content.strip()

            logger.info(f"Aggregated {len(results)} results")
            return aggregated_text

        except Exception as e:
            logger.error(f"Aggregation failed: {str(e)}")
            # Fallback: simple concatenation
            return self._fallback_aggregation(results)

    def _build_aggregation_prompt(self, results: List[str], original_query: str) -> str:
        """Build the aggregation prompt for the LLM."""
        results_text = "\n".join([f"{i+1}. {result}" for i, result in enumerate(results)])

        prompt = f"""You are synthesizing results from multiple business operations into a clear, professional response.

User's Original Query: {original_query}

Task Results:
{results_text}

Create a natural, conversational summary that:
1. Confirms what was accomplished
2. Provides key information from the results
3. Suggests relevant next steps if appropriate
4. Uses a professional but friendly tone
5. Is concise (2-4 sentences typically)

Do not repeat task numbers or technical details unnecessarily. Focus on what matters to the user.

Response:"""

        return prompt

    def _clean_single_result(self, result: str) -> str:
        """Clean up a single result for presentation."""
        # Remove task markers
        if result.startswith("✓") or result.startswith("❌"):
            # Find the colon and get text after it
            colon_idx = result.find(":")
            if colon_idx != -1:
                return result[colon_idx + 1:].strip()
        return result

    def _fallback_aggregation(self, results: List[str]) -> str:
        """Simple fallback if LLM aggregation fails."""
        success_count = sum(1 for r in results if r.startswith("✓"))
        failure_count = sum(1 for r in results if r.startswith("❌"))

        summary = f"Completed {success_count} of {len(results)} tasks"
        if failure_count > 0:
            summary += f" ({failure_count} failed)"
        summary += ".\n\n"

        # Include results
        summary += "Results:\n" + "\n".join(results)

        return summary
