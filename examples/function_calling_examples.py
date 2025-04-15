"""Function calling examples.

This module demonstrates how to use the function calling features of MFCS.
It includes examples of:
1. Generating function calling prompts
2. Parsing function calls from text
3. Using function calling with OpenAI
"""

import os
import json
import openai
from dotenv import load_dotenv
from mfcs.function_calling.function_prompt import FunctionPromptGenerator
from mfcs.function_calling.response_parser import ResponseParser
from mfcs.function_calling import ApiResultManager

# Load environment variables
load_dotenv()

# Configure OpenAI
client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_BASE"))

# Define function schemas
functions = [
    {
        "name": "search_database",
        "description": "Search the database for information",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "The search query"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results to return",
                    "default": 10
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "get_weather",
        "description": "Get the current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "The unit of temperature to use",
                    "default": "celsius"
                }
            },
            "required": ["location"]
        }
    }
]

def example_generate_function_prompt() -> None:
    """Example of generating function calling prompts.
    
    This example shows how to generate function calling prompts
    using the new FunctionPromptGenerator.
    """
    print("\nExample 1: Generate Prompt Templates")
    print("=" * 50)
    
    # Generate prompt template
    template = FunctionPromptGenerator.generate_function_prompt(functions)
    print("\nGenerated Template:")
    print(template)
    
    # Example of how to use the template
    print("\nExample Usage:")
    print("When you need to call a function, use the following format:")
    print("""
<mfcs_call>
<instructions>Search for information about Python programming</instructions>
<call_id>1</call_id>
<name>search_database</name>
<parameters>
{
    "query": "Python programming",
    "limit": 5
}
</parameters>
</mfcs_call>
    """)

def example_parse_function_call() -> None:
    """Example of parsing function calls from text.
    
    This example shows how to parse function calls from text
    using the StreamParser.
    """
    print("\nExample 2: Parse Function Calls")
    print("=" * 50)
    
    # Example text with a function call
    text = """
Here is some information about Python programming.

<mfcs_call>
<instructions>Search for information about Python programming</instructions>
<call_id>1</call_id>
<name>search_database</name>
<parameters>
{
    "query": "Python programming",
    "limit": 5
}
</parameters>
</mfcs_call>

Based on the search results, Python is a versatile programming language.
"""
    
    # Parse the function call
    parser = ResponseParser()
    content, tool_calls = parser.parse_output(text)
    
    # Print the results
    print("\nOriginal Text:")
    print(text)
    print("\nParsed Content:")
    print(content)
    print("\nParsed Tool Calls:")
    for tool_call in tool_calls:
        print(f"Function: {tool_call['name']}")
        print(f"Arguments: {json.dumps(tool_call['arguments'], indent=2)}")

def example_openai_function_calling() -> None:
    """Example of using function calling with OpenAI.
    
    This example shows how to use function calling with OpenAI
    to generate function calls.
    """
    print("\nExample 3: OpenAI Function Calling")
    print("=" * 50)
    
    # Generate prompt template
    prompt_template = FunctionPromptGenerator.generate_function_prompt(functions)
    
    # Create chat completion request
    response = client.chat.completions.create(
        model="qwen-plus-latest",
        messages=[
            {
                "role": "system",
                "content": f"You are a helpful assistant that can search the database and get weather information.\n{prompt_template}"
            },
            {
                "role": "user",
                "content": "What's the weather like in New York and find information about Python programming"
            }
        ]
    )
    
    # Get the response content
    content = response.choices[0].message.content
    
    # Parse the function calls
    parser = ResponseParser()
    parsed_content, tool_calls = parser.parse_output(content)
    
    # Print the results
    print("\nOpenAI Response:")
    print(content)
    print("\nParsed Content:")
    print(parsed_content)
    print("\nParsed Tool Calls:")
    for tool_call in tool_calls:
        print(f"Function: {tool_call['name']}")
        print(f"Arguments: {json.dumps(tool_call['arguments'], indent=2)}")

def main() -> None:
    """Run function calling examples."""
    # Example 1: Basic function calling
    print("Example 1: Basic function calling")
    
    # Generate function calling prompt
    prompt_generator = FunctionPromptGenerator()
    prompt = prompt_generator.generate_function_prompt(functions)
    print("\nGenerated Prompt:")
    print(prompt)
    
    # Example response with function calls
    response = """To provide you with the current weather in New York and information about Python programming, I will first fetch the weather details for New York and then search the database for relevant information on Python programming.
<mfcs_call>
<instructions>Fetching the current weather in New York</instructions>
<call_id>1</call_id>
<name>get_weather</name>
<parameters>
{
  "location": "New York, NY",
  "unit": "fahrenheit"
}
</parameters>
</mfcs_call>
<mfcs_call>
<instructions>Searching for information about Python programming</instructions>
<call_id>2</call_id>
<name>search_database</name>
<parameters>
{
  "query": "Python programming",
  "limit": 5
}
</parameters>
</mfcs_call>"""
    
    # Parse response
    parser = ResponseParser()
    content, tool_calls = parser.parse_output(response)
    
    print("\nParsed Content:")
    print("-" * 50)
    print(content)
    print("-" * 50)
    
    print("\nParsed Tool Calls:")
    print("-" * 50)
    for i, tool_call in enumerate(tool_calls, 1):
        print(f"Tool Call #{i}:")
        print(f"  Instructions: {tool_call['instructions']}")
        print(f"  Call ID: {tool_call['call_id']}")
        print(f"  Name: {tool_call['name']}")
        print(f"  Arguments: {json.dumps(tool_call['arguments'], indent=2)}")
        print("-" * 50)
    
    # Handle API results
    api_manager = ApiResultManager()
    
    # Simulate API responses
    api_manager.add_api_result("1", {
        "temperature": 72,
        "unit": "fahrenheit",
        "description": "Partly cloudy"
    }, "get_weather")
    
    api_manager.add_api_result("2", {
        "results": [
            "Python is a high-level programming language",
            "Python supports multiple programming paradigms",
            "Python has a large standard library"
        ]
    }, "search_database")
    
    # Get and display results
    print("\nAPI Results:")
    print("-" * 50)
    print(api_manager.get_api_results())
    print("-" * 50)

if __name__ == "__main__":
    main() 