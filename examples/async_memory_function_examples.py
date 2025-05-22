"""Async memory function examples.

This module demonstrates how to use memory function features of MFCS asynchronously.
It includes examples of:
1. Basic async memory operations
2. Async memory result handling
3. Async memory function calling with streaming
"""

import os
import json
import asyncio
from openai import AsyncOpenAI
from dotenv import load_dotenv
from mfcs.memory_prompt import MemoryPromptGenerator
from mfcs.response_parser import ResponseParser, MemoryCall
from mfcs.result_manager import ResultManager

# Load environment variables
load_dotenv()

# Configure OpenAI
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_BASE"))

# Define memory APIs
memory_apis = [
    {
        "name": "store_preference",
        "description": "Store user preferences in memory",
        "parameters": {
            "properties": {
                "key": {
                    "type": "string",
                    "description": "The key to store the preference under"
                },
                "value": {
                    "type": "string",
                    "description": "The value to store"
                }
            },
            "required": ["key", "value"]
        }
    },
    {
        "name": "get_preference",
        "description": "Retrieve user preferences from memory",
        "parameters": {
            "properties": {
                "key": {
                    "type": "string",
                    "description": "The key to retrieve the preference for"
                }
            },
            "required": ["key"]
        }
    }
]

async def example_async_memory_function():
    """Example of async memory function calling with streaming.
    
    This example demonstrates how to handle memory function calls in responses asynchronously
    with streaming output.
    """
    print("\nExample: Async Memory Function Calling with Streaming")
    print("=" * 50)
    
    # Generate memory prompt
    memory_prompt = MemoryPromptGenerator.generate_memory_prompt(memory_apis)
    
    # Create chat completion request with memory operations and streaming
    stream = await client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[
            {
                "role": "system",
                "content": memory_prompt
            },
            {
                "role": "user",
                "content": "Remember that I prefer Python programming language and then tell me what you know about my preferences."
            }
        ],
        stream=True,
        stream_options={"include_usage": True}
    )
    
    # Initialize parser and result handler
    response_parser = ResponseParser()
    result_manager = ResultManager()
    
    print("\nStreaming Response:")
    print("-" * 30)
    
    # Process streaming response using stream_parser
    async for delta, call_info, reasoning_content, usage in response_parser.parse_stream_output(stream):
        # Print reasoning content if present
        if reasoning_content:
            print(f"Reasoning: {reasoning_content}")
        
        # Print parsed content (without memory calls)
        if delta:
            print(f"Content: {delta.content} (finish reason: {delta.finish_reason})")
        
        # Handle memory calls
        if call_info and isinstance(call_info, MemoryCall):
            print(f"\nMemory Call:")
            print(f"Instructions: {call_info.instructions}")
            print(f"Memory ID: {call_info.memory_id}")
            print(f"Name: {call_info.name}")
            print(f"Arguments: {json.dumps(call_info.arguments, indent=2)}")
            
            result_manager.add_memory_result(
                name=call_info.name,
                result={"status": "success", "data": f"Simulated async memory for {call_info.name}"},
                memory_id=call_info.memory_id
            )
            
        # Print usage statistics if available
        if usage:
            print(f"\nUsage Statistics:")
            print(f"Prompt tokens: {usage.prompt_tokens}")
            print(f"Completion tokens: {usage.completion_tokens}")
            print(f"Total tokens: {usage.total_tokens}")
    
    # Print final memory results
    print("\nMemory Results:")
    print(result_manager.get_memory_results())

async def example_generate_prompt() -> None:
    """Example of generating prompt templates.
    
    This example shows how to generate different types of prompt templates
    for function calling.
    """
    print("\nExample 1: Generate Prompt Templates")
    print("=" * 50)
    
    # Generate prompt template
    prompt_template = MemoryPromptGenerator.generate_memory_prompt(memory_apis)
    
    print("\nGenerated Prompt Template:")
    print("-" * 50)
    print(prompt_template)
    print("-" * 50)

async def main():
    """Main async function.
    
    Run the async memory function examples with streaming.
    """
    print("Async Memory Function Examples with Streaming")
    print("=" * 50)
    
    # Run examples
    await example_generate_prompt()
    await example_async_memory_function()

if __name__ == "__main__":
    asyncio.run(main())