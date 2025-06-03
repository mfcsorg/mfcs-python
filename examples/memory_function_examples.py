"""Memory function examples.

This module demonstrates how to use memory function features of MFCS.
It includes examples of:
1. Basic memory operations
2. Memory result handling
3. Memory function calling
"""

import os
import json
from openai import OpenAI
from dotenv import load_dotenv
from mfcs.memory_prompt import MemoryPromptGenerator
from mfcs.response_parser import ResponseParser
from mfcs.result_manager import ResultManager

# Load environment variables
load_dotenv()

# Configure OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_BASE"))

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

def example_memory_function():
    """Example of memory function calling.
    
    This example demonstrates how to handle memory function calls in responses.
    """
    print("\nExample: Memory Function Calling")
    print("=" * 50)
    
    # Generate memory prompt
    memory_prompt = MemoryPromptGenerator.generate_memory_prompt(memory_apis)
    
    # Create chat completion request with memory operations
    response = client.chat.completions.create(
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
        ]
    )
    
    # Initialize parser and result handler
    response_parser = ResponseParser()
    result_manager = ResultManager()
    
    # Parse the response
    content, tool_calls, memory_calls, agent_calls = response_parser.parse_output(response.choices[0].message.content)
    
    # Print reasoning content if present
    if response.choices[0].message.reasoning_content:
        print("\nReasoning:")
        print("-" * 30)
        print(response.choices[0].message.reasoning_content)

    # Print content
    if content:
        print("\nContent:")
        print("-" * 30)
        print(content)
    
    # Handle memory calls
    print("\nMemory Calls:")
    print("-" * 30)
    
    # Process all memory calls
    for memory_call in memory_calls:
        print(f"Instructions: {memory_call.instructions}")
        print(f"Memory ID: {memory_call.memory_id}")
        print(f"Name: {memory_call.name}")
        print(f"Arguments: {json.dumps(memory_call.arguments, indent=2)}")
        
        # Simulate memory operation
        result_manager.add_memory_result(
            name=memory_call.name,
            result={"status": "success", "data": f"Simulated memory operation: {memory_call.name}"},
            memory_id=memory_call.memory_id
        )
    
    # Print memory results
    print("\nMemory Results:")
    print(result_manager.get_memory_results())

def example_generate_prompt() -> None:
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

def main():
    """Main function.
    
    Run the memory function examples.
    """
    print("Memory Function Examples")
    print("=" * 50)
    
    # Run examples
    example_generate_prompt()
    example_memory_function()

if __name__ == "__main__":
    main()