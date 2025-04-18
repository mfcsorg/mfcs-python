"""Function calling examples.

This module demonstrates how to use function calling features of MFCS.
It includes examples of:
1. Basic function calling
2. Multiple function calls
3. Function result handling
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from mfcs.function_prompt import FunctionPromptGenerator
from mfcs.response_parser import ResponseParser
from mfcs.result_manager import ResultManager

# Load environment variables
load_dotenv()

# Configure OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_BASE"))

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

def example_basic_function_calling():
    """Example of basic function calling.
    
    This example shows how to use function calling to process a single request
    with potential function calls.
    """
    print("\nExample: Basic Function Calling")
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
                "content": "What's the weather like in Tokyo and find information about Python programming"
            }
        ]
    )
    
    # Initialize parser and result handler
    response_parser = ResponseParser()
    result_manager = ResultManager()
    
    # Parse the response
    content, tool_calls, memory_calls = response_parser.parse_output(response.choices[0].message.content)
    
    # Print content (without function calls)
    if content:
        print("\nContent:")
        print("-" * 30)
        print(content)
    
    # Handle tool calls
    if tool_calls:
        print("\nTool Calls:")
        print("-" * 30)
        for tool_call in tool_calls:
            print(f"Instructions: {tool_call.instructions}")
            print(f"Call ID: {tool_call.call_id}")
            print(f"Name: {tool_call.name}")
            print(f"Arguments: {json.dumps(tool_call.arguments, indent=2)}")
            
            # Simulate tool execution (in real application, this would call actual tools)
            result_manager.add_tool_result(
                call_id=tool_call.call_id,
                result={"status": "success", "data": f"Simulated data for {tool_call.name}"},
                name=tool_call.name
            )
    
    # Print results
    print("\nTool Results:")
    print(result_manager.get_tool_results())

def example_multiple_function_calls():
    """Example of handling multiple function calls.
    
    This example demonstrates how to handle multiple function calls in a single response.
    """
    print("\nExample: Multiple Function Calls")
    print("=" * 50)
    
    # Generate prompt template
    prompt_template = FunctionPromptGenerator.generate_function_prompt(functions)
    
    # Create chat completion request
    response = client.chat.completions.create(
        model="qwen-plus-latest",
        messages=[
            {
                "role": "system",
                "content": f"You are a helpful assistant that can get weather information.\n{prompt_template}"
            },
            {"role": "user", "content": "What's the weather in New York and Tokyo?"}
        ]
    )
    
    # Initialize parser and result handler
    response_parser = ResponseParser()
    result_manager = ResultManager()
    
    # Parse the response
    content, tool_calls, memory_calls = response_parser.parse_output(response.choices[0].message.content)
    
    # Print content (without function calls)
    if content:
        print("\nContent:")
        print("-" * 30)
        print(content)
    
    # Handle tool calls
    if tool_calls:
        print("\nTool Calls:")
        print("-" * 30)
        for tool_call in tool_calls:
            print(f"Instructions: {tool_call.instructions}")
            print(f"Call ID: {tool_call.call_id}")
            print(f"Name: {tool_call.name}")
            print(f"Arguments: {json.dumps(tool_call.arguments, indent=2)}")
            
            # Simulate tool execution
            result_manager.add_tool_result(
                call_id=tool_call.call_id,
                result={"status": "success", "data": f"Simulated data for {tool_call.name}"},
                name=tool_call.name
            )
    
    # Print final results
    print("\nFinal Tool Results:")
    print(result_manager.get_tool_results())

def example_generate_prompt():
    """Example of generating prompt templates.
    
    This example shows how to generate different types of prompt templates
    for function calling.
    """
    print("\nExample: Generate Prompt Templates")
    print("=" * 50)
    
    # Generate prompt template
    prompt_template = FunctionPromptGenerator.generate_function_prompt(functions)
    
    print("\nGenerated Prompt Template:")
    print("-" * 50)
    print(prompt_template)
    print("-" * 50)

def main():
    """Main function.
    
    Run the function calling examples.
    """
    print("Function Calling Examples")
    print("=" * 50)
    
    # Run examples
    example_generate_prompt()
    example_basic_function_calling()
    example_multiple_function_calls()

if __name__ == "__main__":
    main() 