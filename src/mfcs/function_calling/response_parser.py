"""Response parser for function calling."""

import json
import re
from typing import Dict, Any, List, Tuple, Optional, AsyncGenerator


class ResponseParser:
    """Parser for LLM response output.
    
    This class provides methods to parse responses from LLMs
    and extract function calls and content.
    """
    
    def __init__(self):
        """Initialize the response parser."""
        pass
        
    def parse_output(self, output: str) -> Tuple[str, List[Dict[str, Any]]]:
        """Parse the output to extract content and tool calls.
        
        Args:
            output: The output string to parse
            
        Returns:
            Tuple containing:
            - content: The regular content text
            - tool_calls: List of tool call dictionaries
        """
        content = ""
        tool_calls = []
        
        # Split by function call markers
        parts = output.split("<mfcs_call>")
        
        # First part is always content
        content = parts[0].strip()
        
        # Process remaining parts for tool calls
        for part in parts[1:]:
            if "</mfcs_call>" in part:
                tool_call_str, remaining_content = part.split("</mfcs_call>", 1)
                try:
                    # Extract components from XML format
                    instructions = re.search(r"<instructions>(.*?)</instructions>", tool_call_str, re.DOTALL)
                    call_id = re.search(r"<call_id>(.*?)</call_id>", tool_call_str)
                    name = re.search(r"<name>(.*?)</name>", tool_call_str)
                    parameters = re.search(r"<parameters>\s*({.*?})\s*</parameters>", tool_call_str, re.DOTALL)
                    
                    if all([instructions, call_id, name, parameters]):
                        tool_call = {
                            "instructions": instructions.group(1).strip(),
                            "call_id": call_id.group(1).strip(),
                            "name": name.group(1).strip(),
                            "arguments": json.loads(parameters.group(1))
                        }
                        tool_calls.append(tool_call)
                        content += remaining_content.strip()
                    else:
                        content += f"<mfcs_call>{tool_call_str}</mfcs_call>"
                except (json.JSONDecodeError, AttributeError):
                    content += f"<mfcs_call>{tool_call_str}</mfcs_call>"
            else:
                content += f"<mfcs_call>{part}"
        
        return content, tool_calls
    
    async def parse_stream_output(self, stream: AsyncGenerator[Any, None]) -> AsyncGenerator[Tuple[str, Optional[Dict[str, Any]]], None]:
        """Process a stream of chat completion chunks.
        
        Args:
            stream: Async generator yielding chat completion chunks
            
        Returns:
            Async generator yielding tuples of (content, tool_call)
        """
        tool_str = ''
        is_collecting = False
        buffer = ''  # Buffer for accumulating characters
        
        async for chunk in stream:
            # Extract content from OpenAI ChatCompletionChunk
            if hasattr(chunk, 'choices') and chunk.choices and chunk.choices[0].delta.content:
                content = chunk.choices[0].delta.content
            else:
                content = ''
                
            if content:
                # Add current output to buffer
                buffer += content
                
                if not is_collecting:
                    # Check if buffer contains start delimiter
                    if '<mfcs_call>' in buffer:
                        # Split buffer, get content before delimiter
                        parts = buffer.split('<mfcs_call>', 1)
                        if parts[0]:
                            # If there's content before delimiter, output it first
                            # Clean any XML-like tags from content
                            clean_content = self._clean_xml_tags(parts[0])
                            if clean_content.strip():
                                yield clean_content, None
                        
                        # Start collecting tool call content
                        is_collecting = True
                        tool_str = parts[1].lstrip('\n').rstrip('\n')
                        buffer = ''  # Clear buffer
                        continue
                else:
                    # Check if buffer contains end delimiter
                    if '</mfcs_call>' in buffer:
                        # Split buffer, get content before delimiter
                        parts = buffer.split('</mfcs_call>', 1)
                        # Add content before delimiter to tool call string
                        tool_str += parts[0].lstrip('\n').rstrip('\n')
                        
                        # End collection
                        is_collecting = False
                        
                        # Parse the tool call
                        tool_call = self._parse_xml_tool_call(tool_str)
                        
                        # If there's content after delimiter, output it
                        if parts[1]:
                            # Remove possible punctuation
                            content = parts[1].lstrip('.,，。！？!?')
                            # Clean any XML-like tags from content
                            content = self._clean_xml_tags(content)
                            
                            # Check if content contains partial delimiter
                            if '<' in content:
                                # Find last complete sentence
                                last_sentence_end = max(
                                    content.rfind('。'),
                                    content.rfind('？'),
                                    content.rfind('！'),
                                    content.rfind('.'),
                                    content.rfind('?'),
                                    content.rfind('!')
                                )
                                if last_sentence_end > 0:
                                    # Output content up to last complete sentence
                                    yield content[:last_sentence_end + 1], None
                                    # Clear buffer, don't keep any delimiter content
                                    buffer = ''
                                else:
                                    # If no complete sentence found, keep entire content in buffer
                                    buffer = content
                            else:
                                # If no partial delimiter, output entire content
                                if content.strip():
                                    yield content, None
                                # Clear buffer, don't keep any delimiter content
                                buffer = ''
                        else:
                            buffer = ''  # Clear buffer
                        
                        # Yield the tool call
                        if tool_call:
                            yield "", tool_call
                    else:
                        # Check if buffer contains partial delimiter
                        if '<' in buffer:
                            # Find last complete sentence
                            last_sentence_end = max(
                                buffer.rfind('。'),
                                buffer.rfind('？'),
                                buffer.rfind('！'),
                                buffer.rfind('.'),
                                buffer.rfind('?'),
                                buffer.rfind('!')
                            )
                            if last_sentence_end > 0:
                                # Output content up to last complete sentence
                                # Clean any XML-like tags from content
                                clean_content = self._clean_xml_tags(buffer[:last_sentence_end + 1])
                                if clean_content.strip():
                                    yield clean_content, None
                                # Clear buffer, don't keep any delimiter content
                                buffer = ''
                            else:
                                # If no complete sentence found, keep entire buffer
                                continue
                        else:
                            # If no partial delimiter, output entire buffer
                            # Clean any XML-like tags from content
                            clean_content = self._clean_xml_tags(buffer)
                            if clean_content.strip():
                                yield clean_content, None
                            buffer = ''  # Clear buffer
            else:
                yield "", None
    
    def _parse_xml_tool_call(self, text: str) -> Optional[Dict[str, Any]]:
        """Parse an XML format tool call.
        
        Args:
            text: The tool call text to parse
            
        Returns:
            Optional[Dict[str, Any]]: The parsed tool call or None if invalid
        """
        try:
            # Extract instructions
            instructions_match = re.search(r"<instructions>(.*?)</instructions>", text, re.DOTALL)
            if not instructions_match:
                return None
            instructions = instructions_match.group(1).strip()
            
            # Extract call_id
            call_id_match = re.search(r"<call_id>(.*?)</call_id>", text)
            if not call_id_match:
                return None
            call_id = call_id_match.group(1).strip()
            
            # Extract name
            name_match = re.search(r"<name>(.*?)</name>", text)
            if not name_match:
                return None
            name = name_match.group(1).strip()
            
            # Extract parameters
            params_match = re.search(r"<parameters>\s*({.*?})\s*</parameters>", text, re.DOTALL)
            if not params_match:
                return None
            parameters = json.loads(params_match.group(1))
            
            return {
                "instructions": instructions,
                "call_id": call_id,
                "name": name,
                "arguments": parameters
            }
        except Exception as e:
            print(f"Error parsing tool call details: {e}")
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
    