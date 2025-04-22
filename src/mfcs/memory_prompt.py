"""Memory prompt generator."""

import json
from typing import Dict, List, Any


class MemoryPromptGenerator:
    """Generator for memory calling prompts.
    
    This class provides a method to generate generic memory calling prompt templates
    that can be used with various LLMs.
    """
    
    # Common rules for all format types
    COMMON_RULES = """<memory_calling>
You are an AI assistant with personalized memory capabilities. You can use memory tools to store, retrieve, and utilize user's personalized information to provide a more personalized and coherent conversation experience. Please follow these rules:

===Memory Tool Usage Rules===
1. Strictly follow the specified memory tool calling patterns, ensuring all necessary parameters are provided.
2. Only use tools that are explicitly provided in the current environment. Never attempt to call tools that are not available.
3. **When talking to users, never mention tool names.** For example, don't say "I need to use the mfcs_memory tool to store your preferences", instead say "I'll remember this preference of yours".
4. **CRITICAL REQUIREMENT: When the mfcs_memory tool is available, you MUST include at least one <mfcs_memory> tool call in your response.** This requirement applies only when the tool is explicitly provided in the environment.
5. Before calling each memory tool, first explain to the user why you're calling it.
6. After each memory tool usage, always wait for the tool usage result before continuing. Do not assume tool usage success without explicit confirmation.
7. If there are no sequential dependencies between memory operations, you can call multiple memory tools simultaneously.
8. memory_result is automatically returned by the tool call, not user input. Do not treat it as user input. Do not thank the user.

===Memory Tool Interface Usage===
## mfcs_memory
Description: Request to call the memory API. The API defines the input pattern, specifying required and optional parameters.
Parameters:
- instructions: (Required) Content to execute, operations, etc., reminding users what to do
- memory_id: (Required) Memory Tool call ID, starting from 1, incrementing by 1 for each call, using different memory_id for each API call
- name: (Required) Name of the API to execute. Names can only be selected from the following API list. Never generate your own
- parameters: (Required) JSON object containing API input parameters, following the API's input pattern

Example:
<mfcs_memory>
<instructions>Store user's programming language preference</instructions>
<memory_id>1</memory_id>
<name>store_preference</name>
<parameters>
{
  "param1": "value1",
  "param2": "value2"
}
</parameters>
</mfcs_memory>

===Memory Usage Restrictions===
1. The name in mfcs_memory can only be selected from the API list, cannot be generated independently.
2. You should not generate memory_result content. Do not assume tool execution results.
3. Do not place tool calls in markdown.
4. Ensure the accuracy and timeliness of memory content, regularly update outdated information.
5. When storing sensitive information, ensure privacy protection principles are followed.
6. Consider context relevance when using memory, avoid interference from irrelevant information.

===Memory Application Strategy===
1. Active Memory: Identify and store users' important preferences, habits, and needs.
2. Context Association: Establish connections between new memories and existing memories to form a complete user profile.
3. Dynamic Updates: Update memory content promptly to ensure information timeliness.
4. Personalized Responses: Adjust response tone, style, and content based on memory content.
5. Progressive Learning: Continuously enrich and optimize user profiles through ongoing conversations.
6. Privacy Protection: Handle sensitive information carefully, ensure user data security.

</memory_calling>
"""

    @staticmethod
    def validate_memory_schema(memory_schema: Dict[str, Any]) -> None:
        """Validate the memory schema.
        
        Args:
            memory_schema: The memory schema to validate
            
        Raises:
            ValueError: If the memory schema is invalid
        """
        required_fields = ["name", "description"]
        for field in required_fields:
            if field not in memory_schema:
                raise ValueError(f"Memory schema missing required field: {field}")
        
        if "parameters" in memory_schema:
            if not isinstance(memory_schema["parameters"], dict):
                raise ValueError("Memory parameters must be a dictionary")
            
            if "properties" not in memory_schema["parameters"]:
                raise ValueError("Memory parameters missing 'properties' field")

    @classmethod
    def _get_format_instructions(cls) -> str:
        """Get format-specific instructions.
        
        Returns:
            str: Format-specific instructions
        """
        return f"""{cls.COMMON_RULES}"""

    @classmethod
    def generate_memory_prompt(
        cls,
        memory_apis: List[Dict[str, Any]],
    ) -> str:
        """Generate a memory calling prompt template.
        
        This method generates a prompt template that can be used with
        various LLMs that don't have native memory calling support.
        
        Args:
            memory_apis: List of memory API schemas
            
        Returns:
            str: A prompt template for memory calling
        """
        for memory_api in memory_apis:
            cls.validate_memory_schema(memory_api)
        
        memory_apis_str = json.dumps(memory_apis, ensure_ascii=False)

        # format-specific instructions
        template = f'{cls._get_format_instructions()}\n'

        # Build the template
        template += "<memory_list>\n"
        template += memory_apis_str + "\n"
        template += "</memory_list>\n"

        return template
