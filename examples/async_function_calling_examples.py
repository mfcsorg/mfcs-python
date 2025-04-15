"""Async function calling examples.

This module demonstrates how to use async function calling features of MFCS.
It includes examples of:
1. Async streaming with function calling
2. Real-time processing of streaming responses
"""

import os
import json
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
from mfcs.function_calling.function_prompt import FunctionPromptGenerator
from mfcs.function_calling.response_parser import ResponseParser
from mfcs.function_calling.api_result_manager import ApiResultManager

# Load environment variables
load_dotenv()

# Configure OpenAI
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_BASE"))

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

async def example_async_streaming() -> None:
    """Example of async streaming with function calling.
    
    This example shows how to use async streaming with function calling
    to process responses in real-time.
    """
    print("\nExample: Async Streaming")
    print("=" * 50)
    
    # Generate prompt template
    prompt_template = FunctionPromptGenerator.generate_function_prompt(functions)
    
    # Create chat completion request with streaming
    stream = await client.chat.completions.create(
        model="qwen-plus-latest",
        messages=[
            {
                "role": "system",
                "content": f"You are a helpful assistant that can search the database and get weather information.\n{prompt_template}"
            },
            {
                "role": "user",
                "content": "What's the weather like in Tokyo and find information about async programming"
            }
        ],
        stream=True
    )
    
    # Initialize stream parser and result handler
    stream_parser = ResponseParser()
    api_result_manager = ApiResultManager()
    
    print("\nStreaming Response:")
    print("-" * 30)
    
    # Process the stream in real-time
    async for content, tool_call in stream_parser.parse_stream_output(stream):
        # Print parsed content (without function calls)
        if content:
            print(f"Content: {content}")
        
        # Handle tool calls
        if tool_call:
            print(f"\nTool Call:")
            print(f"Instructions: {tool_call['instructions']}")
            print(f"Call ID: {tool_call['call_id']}")
            print(f"Name: {tool_call['name']}")
            print(f"Arguments: {json.dumps(tool_call['arguments'], indent=2)}")
            
            # Simulate tool execution (in real application, this would call actual tools)
            # Add API result with call_id (now required)
            api_result_manager.add_api_result(
                call_id=tool_call["call_id"],
                result={"status": "success", "data": f"Simulated data for {tool_call['name']}"},
                name=tool_call["name"]
            )
    
    # Print results
    print("\nAPI Results:")
    print(api_result_manager.get_api_results())
    
    # Example 2: Multiple function calls
    print("\nExample 2: Multiple function calls")
    messages = [
        {
            "role": "system",
            "content": f"You are a helpful assistant that can get weather information.\n{prompt_template}"
        },
        {"role": "user", "content": "What's the weather in New York and Tokyo?"}
    ]
    
    # Create a new stream for the second example
    stream2 = await client.chat.completions.create(
        model="qwen-plus-latest",
        messages=messages,
        stream=True
    )
    
    # Process the second stream
    async for content, tool_call in stream_parser.parse_stream_output(stream2):
        # Print parsed content (without function calls)
        if content:
            print(f"Content: {content}")
        
        # Handle tool calls
        if tool_call:
            print(f"\nTool Call:")
            print(f"Instructions: {tool_call['instructions']}")
            print(f"Call ID: {tool_call['call_id']}")
            print(f"Name: {tool_call['name']}")
            print(f"Arguments: {json.dumps(tool_call['arguments'], indent=2)}")
            
            # Simulate tool execution
            api_result_manager.add_api_result(
                call_id=tool_call["call_id"],
                result={"status": "success", "data": f"Simulated data for {tool_call['name']}"},
                name=tool_call["name"]
            )
    
    # Print final results
    print("\nFinal API Results:")
    print(api_result_manager.get_api_results())

async def example_generate_prompt() -> None:
    """Example of generating prompt templates.
    
    This example shows how to generate different types of prompt templates
    for function calling.
    """
    print("\nExample 1: Generate Prompt Templates")
    print("=" * 50)
    
    # Generate prompt template
    prompt_template = FunctionPromptGenerator.generate_function_prompt(functions)
    
    print("\nGenerated Prompt Template:")
    print("-" * 50)
    print(prompt_template)
    print("-" * 50)

async def main() -> None:
    """Main function.
    
    Run the async streaming example.
    """
    print("Async Function Calling Examples")
    print("=" * 50)
    
    # Run examples
    await example_generate_prompt()
    await example_async_streaming()

if __name__ == "__main__":
    asyncio.run(main()) 