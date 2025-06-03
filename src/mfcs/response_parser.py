"""Response parser for function calling."""

import json
import re
import logging
from typing import Dict, Any, List, Tuple, Optional, AsyncGenerator, Union
from dataclasses import dataclass

# Set up logger
logger = logging.getLogger(__name__)


@dataclass
class ChoiceDelta:
    """Choice delta information."""
    content: str
    finish_reason: str

@dataclass
class Usage:
    """Usage statistics information."""
    prompt_tokens: int
    completion_tokens: int
    total_tokens: int

@dataclass
class ToolCall:
    """Tool call information."""
    instructions: str
    call_id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class MemoryCall:
    """Memory call information."""
    instructions: str
    memory_id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class AgentCall:
    """Agent call information."""
    instructions: str
    agent_id: str
    name: str
    arguments: Dict[str, Any]


class ResponseParser:
    """Parser for LLM response output.
    
    This class provides methods to parse responses from LLMs
    and extract function calls and content.
    """
    
    # Define commonly used regex patterns
    INSTRUCTIONS_PATTERN = r"<instructions>(.*?)</instructions>"
    CALL_ID_PATTERN = r"<call_id>(.*?)</call_id>"
    MEMORY_ID_PATTERN = r"<memory_id>(.*?)</memory_id>"
    NAME_PATTERN = r"<name>(.*?)</name>"
    PARAMETERS_PATTERN = r"<parameters>\s*({.*?})\s*</parameters>"
    AGENT_ID_PATTERN = r"<agent_id>(.*?)</agent_id>"
    
    def __init__(self):
        """Initialize the response parser."""
        pass
        
    def parse_output(self, output: str) -> Tuple[str, List[ToolCall], List[MemoryCall], List[AgentCall]]:
        """Parse the output to extract content, tool calls, memory calls, and agent calls."""
        content = ""
        tool_calls = []
        memory_calls = []
        agent_calls = []
        
        # Split by function call markers
        parts = output.split("<mfcs_tool>")
        
        # First part is always content
        content = parts[0].strip()
        
        # Process remaining parts for tool calls
        for part in parts[1:]:
            if "</mfcs_tool>" in part:
                tool_call_str, remaining_content = part.split("</mfcs_tool>", 1)
                try:
                    # Extract components from XML format
                    instructions = re.search(self.INSTRUCTIONS_PATTERN, tool_call_str, re.DOTALL)
                    call_id = re.search(self.CALL_ID_PATTERN, tool_call_str)
                    name = re.search(self.NAME_PATTERN, tool_call_str)
                    parameters = re.search(self.PARAMETERS_PATTERN, tool_call_str, re.DOTALL)
                    
                    if all([instructions, call_id, name, parameters]):
                        tool_call = ToolCall(
                            instructions=instructions.group(1).strip(),
                            call_id=call_id.group(1).strip(),
                            name=name.group(1).strip(),
                            arguments=json.loads(parameters.group(1))
                        )
                        tool_calls.append(tool_call)
                        content += remaining_content.strip()
                    else:
                        content += f"<mfcs_tool>{tool_call_str}</mfcs_tool>"
                except (json.JSONDecodeError, AttributeError) as e:
                    logger.warning(f"Error parsing tool call: {e}")
                    content += f"<mfcs_tool>{tool_call_str}</mfcs_tool>"
            else:
                content += f"<mfcs_tool>{part}"
        
        # Split by memory call markers
        parts = content.split("<mfcs_memory>")
        content = parts[0].strip()
        
        # Process remaining parts for memory calls
        for part in parts[1:]:
            if "</mfcs_memory>" in part:
                memory_call_str, remaining_content = part.split("</mfcs_memory>", 1)
                try:
                    # Extract components from XML format
                    instructions = re.search(self.INSTRUCTIONS_PATTERN, memory_call_str, re.DOTALL)
                    memory_id = re.search(self.MEMORY_ID_PATTERN, memory_call_str)
                    name = re.search(self.NAME_PATTERN, memory_call_str)
                    parameters = re.search(self.PARAMETERS_PATTERN, memory_call_str, re.DOTALL)
                    
                    if all([instructions, memory_id, name, parameters]):
                        memory_call = MemoryCall(
                            instructions=instructions.group(1).strip(),
                            memory_id=memory_id.group(1).strip(),
                            name=name.group(1).strip(),
                            arguments=json.loads(parameters.group(1))
                        )
                        memory_calls.append(memory_call)
                        content += remaining_content.strip()
                    else:
                        content += f"<mfcs_memory>{memory_call_str}</mfcs_memory>"
                except (json.JSONDecodeError, AttributeError) as e:
                    logger.warning(f"Error parsing memory call: {e}")
                    content += f"<mfcs_memory>{memory_call_str}</mfcs_memory>"
            else:
                content += f"<mfcs_memory>{part}"
        
        # Split by agent call markers
        parts = content.split("<mfcs_agent>")
        content = parts[0].strip()
        
        # Process remaining parts for agent calls
        for part in parts[1:]:
            if "</mfcs_agent>" in part:
                agent_call_str, remaining_content = part.split("</mfcs_agent>", 1)
                try:
                    # Extract components from XML format
                    instructions = re.search(self.INSTRUCTIONS_PATTERN, agent_call_str, re.DOTALL)
                    agent_id = re.search(self.AGENT_ID_PATTERN, agent_call_str)
                    name = re.search(self.NAME_PATTERN, agent_call_str)
                    parameters = re.search(self.PARAMETERS_PATTERN, agent_call_str, re.DOTALL)
                    
                    if all([instructions, agent_id, name, parameters]):
                        agent_call = AgentCall(
                            instructions=instructions.group(1).strip(),
                            agent_id=agent_id.group(1).strip(),
                            name=name.group(1).strip(),
                            arguments=json.loads(parameters.group(1))
                        )
                        agent_calls.append(agent_call)
                        content += remaining_content.strip()
                    else:
                        content += f"<mfcs_agent>{agent_call_str}</mfcs_agent>"
                except (json.JSONDecodeError, AttributeError) as e:
                    logger.warning(f"Error parsing agent call: {e}")
                    content += f"<mfcs_agent>{agent_call_str}</mfcs_agent>"
            else:
                content += f"<mfcs_agent>{part}"
        
        return content, tool_calls, memory_calls, agent_calls
    
    async def parse_stream_output(self, stream: AsyncGenerator[Any, None]) -> AsyncGenerator[Tuple[Optional[ChoiceDelta], Optional[Union[ToolCall, MemoryCall, AgentCall]], Optional[str], Optional[Usage]], None]:
        """Process a stream of chat completion chunks.
        
        Args:
            stream: Async generator yielding chat completion chunks
            
        Returns:
            Async generator yielding tuples of (content, call_info, reasoning_content, usage)
            where:
            - choice_delta: Either None, a ChoiceDelta
            - call_info: Either None, a ToolCall, or a MemoryCall
            - reasoning_content: The reasoning content if present, None otherwise
            - usage: Usage statistics if present, None otherwise
        """
        buffer = ''
        tool_buffer = ''
        memory_buffer = ''
        agent_buffer = ''
        is_collecting_tool = False
        is_collecting_memory = False
        is_collecting_agent = False
        usage = None
        finish_reason = None
        
        async for chunk in stream:
            # Extract content and reasoning_content from OpenAI ChatCompletionChunk
            content = ''
            reasoning_content = ''
            
            if hasattr(chunk, 'choices') and chunk.choices:
                if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                if hasattr(chunk.choices[0].delta, 'reasoning_content') and chunk.choices[0].delta.reasoning_content:
                    reasoning_content = chunk.choices[0].delta.reasoning_content
                    
                # Capture finish_reason if present
                if hasattr(chunk.choices[0], 'finish_reason') and chunk.choices[0].finish_reason:
                    finish_reason = chunk.choices[0].finish_reason
                    
            # Extract usage if present
            if hasattr(chunk, 'usage'):
                usage = Usage(
                    prompt_tokens=getattr(chunk.usage, 'prompt_tokens', 0),
                    completion_tokens=getattr(chunk.usage, 'completion_tokens', 0),
                    total_tokens=getattr(chunk.usage, 'total_tokens', 0)
                )
                
            if content is None and reasoning_content is None:
                continue
                
            # First yield reasoning_content if present
            if reasoning_content:
                yield None, None, reasoning_content, None
                
            # Add current content to appropriate buffer
            if is_collecting_tool:
                tool_buffer += content
            elif is_collecting_memory:
                memory_buffer += content
            elif is_collecting_agent:
                agent_buffer += content
            else:
                buffer += content
            
            # Process buffers based on current state
            if is_collecting_tool:
                # Check for end of tool call
                if '</mfcs_tool>' in tool_buffer:
                    parts = tool_buffer.split('</mfcs_tool>', 1)
                    tool_content = parts[0]
                    remaining = parts[1] if len(parts) > 1 else ''
                    
                    # Parse the tool call
                    tool_call = self._parse_xml_tool_call(tool_content)
                    if tool_call:
                        yield None, tool_call, None, None
                    
                    # Reset tool collection state
                    is_collecting_tool = False
                    tool_buffer = ''
                    
                    # Process any remaining content
                    if remaining:
                        buffer = remaining
            elif is_collecting_memory:
                # Check for end of memory
                if '</mfcs_memory>' in memory_buffer:
                    parts = memory_buffer.split('</mfcs_memory>', 1)
                    memory_content = parts[0]
                    remaining = parts[1] if len(parts) > 1 else ''
                    
                    # Parse the memory content
                    memory_call = self._parse_xml_memory(memory_content)
                    if memory_call:
                        yield None, memory_call, None, None
                    
                    # Reset memory collection state
                    is_collecting_memory = False
                    memory_buffer = ''
                    
                    # Process any remaining content
                    if remaining:
                        buffer = remaining
            elif is_collecting_agent:
                if '</mfcs_agent>' in agent_buffer:
                    parts = agent_buffer.split('</mfcs_agent>', 1)
                    agent_content = parts[0]
                    remaining = parts[1] if len(parts) > 1 else ''
                    agent_call = self._parse_xml_agent(agent_content)
                    if agent_call:
                        yield None, agent_call, None, None
                    is_collecting_agent = False
                    agent_buffer = ''
                    if remaining:
                        buffer = remaining
            else:
                # Check for start of tool call or memory
                if '<mfcs_tool>' in buffer:
                    parts = buffer.split('<mfcs_tool>', 1)
                    
                    # Output content before tool call
                    if parts[0]:
                        yield ChoiceDelta(content=parts[0], finish_reason=None), None, None, None
                    
                    # Start collecting tool call
                    is_collecting_tool = True
                    tool_buffer = parts[1] if len(parts) > 1 else ''
                    buffer = ''
                elif '<mfcs_memory>' in buffer:
                    parts = buffer.split('<mfcs_memory>', 1)
                    
                    # Output content before memory
                    if parts[0]:
                        yield ChoiceDelta(content=parts[0], finish_reason=None), None, None, None
                    
                    # Start collecting memory
                    is_collecting_memory = True
                    memory_buffer = parts[1] if len(parts) > 1 else ''
                    buffer = ''
                elif '<mfcs_agent>' in buffer:
                    parts = buffer.split('<mfcs_agent>', 1)
                    if parts[0]:
                        yield ChoiceDelta(content=parts[0], finish_reason=None), None, None, None
                    is_collecting_agent = True
                    agent_buffer = parts[1] if len(parts) > 1 else ''
                    buffer = ''
                else:
                    # Optimization: Check if it contains the start of a special marker
                    if '<' in buffer:
                        # If it contains < symbol, it might be the start of a special marker, keep it in buffer
                        continue
                    # Otherwise output content immediately
                    if buffer:
                        yield ChoiceDelta(content=buffer, finish_reason=None), None, None, None
                        buffer = ''

        # Yield any remaining content in buffer
        if buffer:
            yield ChoiceDelta(content=buffer, finish_reason=None), None, None, None
            
        # Yield finish reason at the end if available
        if finish_reason:
            yield ChoiceDelta(content=None, finish_reason=finish_reason), None, None, None
            
        # Yield usage information at the end if available
        if usage:
            yield None, None, None, usage
    
    def _parse_xml_tool_call(self, text: str) -> Optional[ToolCall]:
        """Parse an XML format tool call.
        
        Args:
            text: The tool call text to parse
            
        Returns:
            Optional[ToolCall]: The parsed tool call or None if invalid
        """
        try:
            # Extract components using helper method
            components = self._extract_xml_components(
                text, 
                instructions_pattern=self.INSTRUCTIONS_PATTERN,
                id_pattern=self.CALL_ID_PATTERN,
                name_pattern=self.NAME_PATTERN,
                parameters_pattern=self.PARAMETERS_PATTERN
            )
            
            if not components:
                return None
                
            instructions, id_value, name, parameters = components
            
            return ToolCall(
                instructions=instructions,
                call_id=id_value,
                name=name,
                arguments=parameters
            )
        except Exception as e:
            logger.error(f"Error parsing tool call details: {e}")
            return None
    
    def _clean_xml_tags(self, text: str) -> str:
        """Remove XML-like tags from text.
        
        Args:
            text: Text that may contain XML-like tags
            
        Returns:
            Cleaned text with XML-like tags removed
        """
        # Remove common XML-like tags
        cleaned = re.sub(r'<instructions>.*?</instructions>', '', text, flags=re.DOTALL)
        cleaned = re.sub(r'<call_id>.*?</call_id>', '', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'<name>.*?</name>', '', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'<parameters>.*?</parameters>', '', cleaned, flags=re.DOTALL)
        cleaned = re.sub(r'<mfcs_call>.*?</mfcs_call>', '', cleaned, flags=re.DOTALL)
        
        # Remove any remaining XML-like tags
        cleaned = re.sub(r'<[^>]*>', '', cleaned)
        
        # Clean up any extra whitespace and normalize spaces
        cleaned = ' '.join(cleaned.split())
        
        return cleaned
    
    def _parse_xml_memory(self, text: str) -> Optional[MemoryCall]:
        """Parse an XML format memory.
        
        Args:
            text: The memory text to parse
            
        Returns:
            Optional[MemoryCall]: The parsed memory or None if invalid
        """
        try:
            # Extract components using helper method
            components = self._extract_xml_components(
                text, 
                instructions_pattern=self.INSTRUCTIONS_PATTERN,
                id_pattern=self.MEMORY_ID_PATTERN,
                name_pattern=self.NAME_PATTERN,
                parameters_pattern=self.PARAMETERS_PATTERN
            )
            
            if not components:
                return None
                
            instructions, id_value, name, parameters = components
            
            return MemoryCall(
                instructions=instructions,
                memory_id=id_value,
                name=name,
                arguments=parameters
            )
        except Exception as e:
            logger.error(f"Error parsing memory details: {e}")
            return None
            
    def _parse_xml_agent(self, text: str) -> Optional[AgentCall]:
        """Parse an XML format agent call.
        Args:
            text: The agent call text to parse
        Returns:
            Optional[AgentCall]: The parsed agent call or None if invalid
        """
        try:
            components = self._extract_xml_components(
                text,
                instructions_pattern=self.INSTRUCTIONS_PATTERN,
                id_pattern=self.AGENT_ID_PATTERN,
                name_pattern=self.NAME_PATTERN,
                parameters_pattern=self.PARAMETERS_PATTERN
            )
            if not components:
                return None
            instructions, id_value, name, parameters = components
            return AgentCall(
                instructions=instructions,
                agent_id=id_value,
                name=name,
                arguments=parameters
            )
        except Exception as e:
            logger.error(f"Error parsing agent details: {e}")
            return None

    def _extract_xml_components(
        self, 
        text: str, 
        instructions_pattern: str,
        id_pattern: str,
        name_pattern: str,
        parameters_pattern: str
    ) -> Optional[Tuple[str, str, str, Dict[str, Any]]]:
        """Extract XML components from text using provided patterns.
        
        Args:
            text: The text to extract components from
            instructions_pattern: Pattern for instructions
            id_pattern: Pattern for ID (call_id or memory_id)
            name_pattern: Pattern for name
            parameters_pattern: Pattern for parameters
            
        Returns:
            Optional tuple of (instructions, id_value, name, parameters) or None if extraction fails
        """
        # Extract instructions
        instructions_match = re.search(instructions_pattern, text, re.DOTALL)
        if not instructions_match:
            return None
        instructions = instructions_match.group(1).strip()
        
        # Extract ID
        id_match = re.search(id_pattern, text)
        if not id_match:
            return None
        id_value = id_match.group(1).strip()
        
        # Extract name
        name_match = re.search(name_pattern, text)
        if not name_match:
            return None
        name = name_match.group(1).strip()
        
        # Extract parameters
        params_match = re.search(parameters_pattern, text, re.DOTALL)
        if not params_match:
            return None
        parameters = json.loads(params_match.group(1))
        
        return instructions, id_value, name, parameters
