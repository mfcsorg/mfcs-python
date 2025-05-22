"""
Result manager for handling LLM responses, tool calls and memory operations.
"""

from typing import Dict, Any, Optional, List
import json
from dataclasses import dataclass, field


@dataclass
class ResultManager:
    """
    Manages tool and memory results and formats them for MFCS.
    
    This class is responsible for:
    1. Storing tool and memory results
    2. Formatting tool and memory results for MFCS
    3. Managing the lifecycle of results (adding, retrieving, clearing)
    """
    
    tool_results: Dict[str, Any] = field(default_factory=dict)
    tool_names: Dict[str, str] = field(default_factory=dict)
    memory_results: Dict[str, Any] = field(default_factory=dict)
    memory_names: Dict[str, str] = field(default_factory=dict)
    agent_results: Dict[str, Any] = field(default_factory=dict)
    agent_names: Dict[str, str] = field(default_factory=dict)
    
    def add_tool_result(self, name: str, result: Any, call_id: str) -> None:
        """
        Add a tool result.
        
        Args:
            name: Name of the tool call
            result: The result of the tool call
            call_id: ID of the tool call
            
        Raises:
            ValueError: If call_id is empty or name is empty
        """
        if not call_id or not name:
            raise ValueError("call_id and name cannot be empty")
            
        self.tool_results[call_id] = result
        self.tool_names[call_id] = name
    
    def add_memory_result(self, name: str, result: Any, memory_id: str) -> None:
        """
        Add a memory result.
        
        Args:
            name: Type of memory name
            result: The result of the memory operation
            memory_id: ID of the memory operation
            
        Raises:
            ValueError: If memory_id is empty or name is empty
        """
        if not memory_id or not name:
            raise ValueError("memory_id and name cannot be empty")
            
        self.memory_results[memory_id] = result
        self.memory_names[memory_id] = name
    
    def add_agent_result(self, name: str, result: Any, agent_id: str) -> None:
        """
        Add an agent result.
        Args:
            name: Type of agent name
            result: The result of the agent operation
            agent_id: ID of the agent operation
        Raises:
            ValueError: If agent_id is empty or name is empty
        """
        if not agent_id or not name:
            raise ValueError("agent_id and name cannot be empty")
        self.agent_results[agent_id] = result
        self.agent_names[agent_id] = name
    
    def get_tool_results(self) -> str:
        """Get and format tool results for MFCS, then clear the results.
        
        Returns:
            Formatted string of tool results
        """
        if not self.tool_results:
            return ""
        
        formatted: List[str] = ["<tool_result>"]
        for call_id, result in self.tool_results.items():
            tool_name = self.tool_names.get(call_id, "unknown")
            result_str = self._convert_to_string(result)
            formatted.append(f"{{call_id: {call_id}, name: {tool_name}}} {result_str}")
        formatted.append("</tool_result>")
        
        # Clear results after formatting
        self._clear_tool_results()
        
        return "\n".join(formatted)
    
    def get_memory_results(self) -> str:
        """Get and format memory results for MFCS, then clear the results.
        
        Returns:
            Formatted string of memory results
        """
        if not self.memory_results:
            return ""
        
        formatted: List[str] = ["<memory_result>"]
        for memory_id, result in self.memory_results.items():
            name = self.memory_names.get(memory_id, "unknown")
            result_str = self._convert_to_string(result)
            formatted.append(f"{{memory_id: {memory_id}, name: {name}}} {result_str}")
        formatted.append("</memory_result>")
        
        # Clear results after formatting
        self._clear_memory_results()
        
        return "\n".join(formatted)
    
    def get_agent_results(self) -> str:
        """Get and format agent results for MFCS, then clear the results.
        Returns:
            Formatted string of agent results
        """
        if not self.agent_results:
            return ""
        formatted: List[str] = ["<agent_result>"]
        for agent_id, result in self.agent_results.items():
            name = self.agent_names.get(agent_id, "unknown")
            result_str = self._convert_to_string(result)
            formatted.append(f"{{agent_id: {agent_id}, name: {name}}} {result_str}")
        formatted.append("</agent_result>")
        self._clear_agent_results()
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
            return json.dumps(result, ensure_ascii=False)
        except (TypeError, ValueError):
            # If JSON serialization fails, use str() as fallback
            return str(result)
    
    def _clear_tool_results(self) -> None:
        """Clear all tool results."""
        self.tool_results.clear()
        self.tool_names.clear()
    
    def _clear_memory_results(self) -> None:
        """Clear all memory results."""
        self.memory_results.clear()
        self.memory_names.clear()
    
    def _clear_agent_results(self) -> None:
        """Clear all agent results."""
        self.agent_results.clear()
        self.agent_names.clear()
        
    def get_tool_result(self, call_id: str) -> Optional[Any]:
        """
        Get a specific tool result by call_id.
        
        Args:
            call_id: The ID of the tool call
            
        Returns:
            The tool result if found, None otherwise
        """
        return self.tool_results.get(call_id)
        
    def get_memory_result(self, memory_id: str) -> Optional[Any]:
        """
        Get a specific memory result by memory_id.
        
        Args:
            memory_id: The ID of the memory operation
            
        Returns:
            The memory result if found, None otherwise
        """
        return self.memory_results.get(memory_id)
    
    def get_agent_result(self, agent_id: str) -> Optional[Any]:
        """
        Get a specific agent result by agent_id.
        Args:
            agent_id: The ID of the agent operation
        Returns:
            The agent result if found, None otherwise
        """
        return self.agent_results.get(agent_id)
