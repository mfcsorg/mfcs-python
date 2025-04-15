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
3.**When talking to users, never mention tool names.** For example, instead of saying "I need to use the mfcs_call tool to edit your file", say "I will edit your file".
4. Only call tools when necessary. If the user's task is general or you already know the answer, simply respond without calling tools.
5. Before calling each tool, first explain to the user why you are calling it.
6. After each tool use, always wait for the tool usage result before continuing. Do not assume tool usage success without explicit confirmation.
7. You can call multiple APIs simultaneously if they don't have sequential dependencies
8. mfcs_result is automatically returned by tool calls and is not user input. Do not treat it as user input. Do not thank the user.

===Interface Usage===
## mfcs_call
Description: Request to call an API. The API defines the input pattern, specifying required and optional parameters.
Parameters:
- instructions: (required) Content to be executed, actions, etc., reminding users what to do
- call_id: (required) Tool call ID, starting from 1, +1 for each call, use different call_id for each api call
- name: (required) Name of the API to execute. Names can only be selected from the following api list. Never generate your own
- parameters: (required) A JSON object containing API input parameters, following the API's input pattern
Example:
<mfcs_call>
<instructions>xxx</instructions>
<call_id>call api index</call_id>
<name>api name here</name>
<parameters>
{
  "param1": "value1",
  "param2": "value2"
}
</parameters>
</mfcs_call>

===Restrictions===
1. The name in mfcs_call can only be selected from the api list, cannot be self-generated.
2. You should not generate mfcs_result content. do not assume tool execution result.
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
            functions: List of function schemas
            
        Returns:
            str: A prompt template for function calling
        """
        for function in functions:
            cls.validate_function_schema(function)
        
        functions_str = json.dumps(functions)

        # format-specific instructions
        template = f'{cls._get_format_instructions()}\n\n'

        # Build the template
        template += "<api_list>\n"
        template += functions_str + "\n"
        template += "</api_list>\n"        

        return template
