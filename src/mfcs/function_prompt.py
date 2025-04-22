"""Function prompt generator."""

import json
from typing import Dict, List, Any


class FunctionPromptGenerator:
    """Generator for function calling prompts.
    
    This class provides a method to generate generic function calling prompt templates
    that can be used with various LLMs.
    """
    
    # Common rules for all format types
    COMMON_RULES = """<tool_calling>
You can use tools to solve tasks. Follow these rules about tool calling:
1. Always strictly follow the specified tool calling pattern and ensure all necessary parameters are provided.
2. Conversations may reference tools that are no longer available. Never call tools that are not explicitly provided.
3.**When talking to users, never mention tool names.** For example, instead of saying "I need to use the edit_tool to edit your file", say "I will edit your file".
4. Only call tools when necessary. If the user's task is general or you already know the answer, simply respond without calling tools.
5. Before calling each tool, first explain to the user why you are calling it.
6. After each tool use, always wait for the tool usage result before continuing. Do not assume tool usage success without explicit confirmation.
7. You can call multiple tools simultaneously if they don't have sequential dependencies
8. tool_result is automatically returned by tool calls and is not user input. Do not treat it as user input. Do not thank the user.

===Interface Usage===
## mfcs_tool
Description: Request to call an tool. The tool defines the input pattern, specifying required and optional parameters.
Parameters:
- instructions: (required) Content to be executed, actions, etc., reminding users what to do
- call_id: (required) Tool call ID, starting from 1, +1 for each call, use different call_id for each tool call
- name: (required) Name of the tool to execute. Names can only be selected from the following tool list. Never generate your own
- parameters: (required) A JSON object containing tool input parameters, following the tool's input pattern
Example:
<mfcs_tool>
<instructions>what to do</instructions>
<call_id>call tool index</call_id>
<name>tool name here</name>
<parameters>
{
  "param1": "value1",
  "param2": "value2"
}
</parameters>
</mfcs_tool>

===Restrictions===
1. The name in mfcs_tool can only be selected from the tool list, cannot be self-generated.
2. You should not generate tool_result content. do not assume tool execution result.
3. Do not put tool calls in markdown.

</tool_calling>
"""

    @staticmethod
    def validate_function_schema(function_schema: Dict[str, Any]) -> None:
        """Validate the function schema.
        
        Args:
            function_schema: The function schema to validate
            
        Raises:
            ValueError: If the function schema is invalid
        """
        required_fields = ["name", "description"]
        for field in required_fields:
            if field not in function_schema:
                raise ValueError(f"Function schema missing required field: {field}")
        
        if "parameters" in function_schema:
            if not isinstance(function_schema["parameters"], dict):
                raise ValueError("Function parameters must be a dictionary")
            
            if "properties" not in function_schema["parameters"]:
                raise ValueError("Function parameters missing 'properties' field")

    @classmethod
    def _get_format_instructions(cls) -> str:
        """Get format-specific instructions.
        
        Returns:
            str: Format-specific instructions
        """
        return f"""{cls.COMMON_RULES}"""

    @classmethod
    def generate_function_prompt(
        cls,
        functions: List[Dict[str, Any]],
    ) -> str:
        """Generate a function calling prompt template.
        
        This method generates a prompt template that can be used with
        various LLMs that don't have native function calling support.
        
        Args:
            functions: List of function schemas. Supports two formats:
                1. Format with nested 'function' key:
                   [{"type": "function", "function": {"name": "...", "description": "...", "parameters": {...}}}]
                2. Format with flat structure:
                   [{"type": "function", "name": "...", "description": "...", "parameters": {...}}]
            
        Returns:
            str: A prompt template for function calling
        """
        # Normalize function schemas to a consistent format
        normalized_functions = []
        for function in functions:
            # Handle format with nested 'function' key
            if "function" in function and isinstance(function["function"], dict):
                normalized_functions.append(function["function"])
            # Handle format with flat structure
            else:
                normalized_functions.append(function)
        
        # Validate each normalized function schema
        for function in normalized_functions:
            cls.validate_function_schema(function)
        
        functions_str = json.dumps(normalized_functions, ensure_ascii=False)

        # format-specific instructions
        template = f'{cls._get_format_instructions()}\n'

        # Build the template
        template += "<tool_list>\n"
        template += functions_str + "\n"
        template += "</tool_list>\n"

        return template
