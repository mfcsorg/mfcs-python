"""
API result manager for handling LLM responses and tool calls.
"""

from typing import Dict, Any
import json


class ApiResultManager:
    """
    Manages API results and formats them for MFCS.
    
    This class is responsible for:
    1. Storing API results
    2. Formatting API results for MFCS
    """
    
    def __init__(self):
        """Initialize the API result manager."""
        self.api_results: Dict[str, Any] = {}
        self.function_names: Dict[str, str] = {}
    
    def add_api_result(self, name: str, result: Any, call_id: str) -> None:
        """
        Add an API result.
        
        Args:
            name: Name of the API call
            result: The result of the API call
            call_id: ID of the tool call
        """
        self.api_results[call_id] = result
        self.function_names[call_id] = name
    
    def get_api_results(self) -> str:
        """Get and format API results for MFCS, then clear the results.
        
        Returns:
            Formatted string of API results
        """
        if not self.api_results:
            return "<api_result>No results available</api_result>"
        
        formatted = ["<api_result>"]
        for call_id, result in self.api_results.items():
            function_name = self.function_names.get(call_id, "unknown")
            formatted.append(f"{{call_id: {call_id}, name: {function_name}}} {self._convert_to_string(result)}")
        formatted.append("</api_result>")
        
        # Clear results after formatting
        self._clear_results()
        
        return "\n".join(formatted)
    
    def _convert_to_string(self, result: Any) -> str:
        """
        Convert any result to a string representation.
        
        Args:
            result: The result to convert
            
        Returns:
            String representation of the result
        """
        if result is None:
            return "null"
        
        try:
            # Try JSON serialization first
            return json.dumps(result)
        except (TypeError, ValueError):
            # If JSON serialization fails, use str() as fallback
            return str(result)
    
    def _clear_results(self) -> None:
        """Clear all API results."""
        self.api_results.clear()
        self.function_names.clear() 