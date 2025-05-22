"""Agent prompt generator."""

import json
from typing import Dict, List, Any


class AgentPromptGenerator:
    """Generator for agent calling prompts.
    
    This class provides a method to generate generic agent calling prompt templates
    that can be used with various LLMs.
    """
    
    # Common rules for all format types
    COMMON_RULES = """<agent_calling>
You are an AI assistant with personalized agent capabilities. You can use agent APIs to store, retrieve, and utilize user's personalized information to provide a more personalized and coherent conversation experience. Please follow these rules:

===Agent API Usage Rules===
1. Strictly follow the specified agent API calling patterns, ensuring all necessary parameters are provided.
2. Only use agent APIs that are explicitly provided in the current environment. Never attempt to call agent APIs that are not available.
3. **When talking to users, never mention API names.** For example, don't say "I need to use the mfcs_agent API to store your preferences", instead say "I'll remember this preference of yours".
4. **CRITICAL REQUIREMENT: When the mfcs_agent API is available, you MUST include at least one <mfcs_agent> API call in your response.** This requirement applies only when the API is explicitly provided in the environment.
5. Before calling each agent API, first explain to the user why you're calling it.
6. After each agent API usage, always wait for the API usage result before continuing. Do not assume API usage success without explicit confirmation.
7. If there are no sequential dependencies between agent API operations, you can call multiple agent APIs simultaneously.
8. agent_result is automatically returned by the API call, not user input. Do not treat it as user input. Do not thank the user.

===Agent API Interface Usage===
## mfcs_agent
Description: Request to call the agent API. The API defines the input pattern, specifying required and optional parameters.
Parameters:
- instructions: (Required) Content to execute, operations, etc., reminding users what to do
- agent_id: (Required) Agent API call ID, starting from 1, incrementing by 1 for each call, using different agent_id for each API call
- name: (Required) Name of the API to execute. Names can only be selected from the following API list. Never generate your own
- parameters: (Required) JSON object containing API input parameters, following the API's input pattern

Example:
<mfcs_agent>
<instructions>Store user's programming language preference</instructions>
<agent_id>1</agent_id>
<name>store_preference</name>
<parameters>
{
  "param1": "value1",
  "param2": "value2"
}
</parameters>
</mfcs_agent>

===Agent API Usage Restrictions===
1. The name in mfcs_agent can only be selected from the API list, cannot be generated independently.
2. You should not generate agent_result content. Do not assume API execution results.
3. Do not place API calls in markdown.
4. Ensure the accuracy and timeliness of agent content, regularly update outdated information.
5. When storing sensitive information, ensure privacy protection principles are followed.
6. Consider context relevance when using agent, avoid interference from irrelevant information.

===Agent Application Strategy===
1. Active Agent: Identify and store users' important preferences, habits, and needs.
2. Context Association: Establish connections between new agents and existing agents to form a complete user profile.
3. Dynamic Updates: Update agent content promptly to ensure information timeliness.
4. Personalized Responses: Adjust response tone, style, and content based on agent content.
5. Progressive Learning: Continuously enrich and optimize user profiles through ongoing conversations.
6. Privacy Protection: Handle sensitive information carefully, ensure user data security.

</agent_calling>
"""

    @staticmethod
    def validate_agent_schema(agent_schema: Dict[str, Any]) -> None:
        """Validate the agent schema.
        
        Args:
            agent_schema: The agent schema to validate
            
        Raises:
            ValueError: If the agent schema is invalid
        """
        required_fields = ["name", "description"]
        for field in required_fields:
            if field not in agent_schema:
                raise ValueError(f"Agent schema missing required field: {field}")
        
        if "parameters" in agent_schema:
            if not isinstance(agent_schema["parameters"], dict):
                raise ValueError("Agent parameters must be a dictionary")
            
            if "properties" not in agent_schema["parameters"]:
                raise ValueError("Agent parameters missing 'properties' field")

    @classmethod
    def _get_format_instructions(cls) -> str:
        """Get format-specific instructions.
        
        Returns:
            str: Format-specific instructions
        """
        return f"{cls.COMMON_RULES}"

    @classmethod
    def generate_agent_prompt(
        cls,
        agent_apis: List[Dict[str, Any]],
    ) -> str:
        """Generate an agent calling prompt template.
        
        This method generates a prompt template that can be used with
        various LLMs that don't have native agent calling support.
        
        Args:
            functions: List of function schemas. Supports two formats:
                1. Format with nested 'function' key:
                   [{"type": "function", "function": {"name": "...", "description": "...", "parameters": {...}}}]
                2. Format with flat structure:
                   [{"type": "function", "name": "...", "description": "...", "parameters": {...}}]
            
        Returns:
            str: A prompt template for agent calling
        """
        # Normalize function schemas to a consistent format
        normalized_agent_apis = []
        for agent_api in agent_apis:
            # Handle format with nested 'function' key
            if "function" in agent_api and isinstance(agent_api["function"], dict):
                normalized_agent_apis.append(agent_api["function"])
            # Handle format with flat structure
            else:
                normalized_agent_apis.append(agent_api)
        
        # Validate each normalized function schema
        for agent_api in normalized_agent_apis:
            cls.validate_agent_schema(agent_api)
        
        agent_apis_str = json.dumps(normalized_agent_apis, ensure_ascii=False)

        # format-specific instructions
        template = f'{cls._get_format_instructions()}\n'

        # Build the template
        template += "<agent_list>\n"
        template += agent_apis_str + "\n"
        template += "</agent_list>\n"

        return template
