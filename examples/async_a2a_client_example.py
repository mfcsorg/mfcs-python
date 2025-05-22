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
from python_a2a import A2AClient, Message, TextContent, MessageRole
from mfcs.agent_prompt import AgentPromptGenerator
from mfcs.response_parser import ResponseParser, AgentCall
from mfcs.result_manager import ResultManager

# Load environment variables
load_dotenv()

# Configure OpenAI
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_BASE"))

# A2A client
a2a_client = A2AClient("http://localhost:8000/a2a")

# Define function schemas
functions1 = [
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

# Define function schemas
functions2 = [
    {
        "type": "function",
        "function": {
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
        }
    },
    {
        "type": "function",
        "function": {
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
    }
]


async def example_async_streaming() -> None:
    """Example of async streaming with A2A.
    
    This example shows how to use async streaming with A2A
    to process responses in real-time.
    """
    print("\nExample: A2A Async Streaming")
    print("=" * 50)
    
    # Generate prompt template
    prompt_template1 = AgentPromptGenerator.generate_agent_prompt(functions1)
    
    # Create chat completion request with streaming
    stream = await client.chat.completions.create(
        model="deepseek-reasoner",
        messages=[
            {
                "role": "system",
                "content": f"You are a helpful assistant that can search the database and get weather information.\n{prompt_template1}"
            },
            {
                "role": "user",
                "content": "What is 1+1 equal to? What's the weather like in Tokyo? Please explain in detail respectively."
            }
        ],
        stream=True,
        stream_options={"include_usage": True}
    )
    
    # Initialize stream parser and result handler
    stream_parser = ResponseParser()
    result_manager = ResultManager()
    
    print("\nStreaming Response:")
    print("-" * 30)
    
    # Process the stream in real-time
    async for delta, call_info, reasoning_content, usage in stream_parser.parse_stream_output(stream):
        # Print reasoning content if present
        if reasoning_content:
            print(f"Reasoning: {reasoning_content}")

        # Print parsed content (without function calls)
        if delta:
            print(f"Content: {delta.content} (finish reason: {delta.finish_reason})")
        
        # Handle tool calls
        if call_info and isinstance(call_info, AgentCall):
            print(f"\nTool Call:")
            print(f"Instructions: {call_info.instructions}")
            print(f"Agent ID: {call_info.agent_id}")
            print(f"Name: {call_info.name}")
            print(f"Arguments: {json.dumps(call_info.arguments, indent=2)}")
            
            # A2A tool execution
            messages = Message(
                role=MessageRole.USER,
                content=TextContent(text=json.dumps(call_info.arguments))
            )
            response = a2a_client.send_message(messages)

            # Add API result with call_id (now required)
            result_manager.add_agent_result(
                name=call_info.name,
                result=json.loads(response.content.text),
                agent_id=call_info.agent_id
            )
            
        # Print usage statistics if available
        if usage:
            print(f"\nUsage Statistics:")
            print(f"Prompt tokens: {usage.prompt_tokens}")
            print(f"Completion tokens: {usage.completion_tokens}")
            print(f"Total tokens: {usage.total_tokens}")
    
    # Print results
    print("\nTool Results:")
    print(result_manager.get_agent_results())

    # Generate prompt template
    prompt_template2 = AgentPromptGenerator.generate_agent_prompt(functions2)
    
    # Example 2: Multiple function calls
    print("\nExample 2: Multiple function calls")
    messages = [
        {
            "role": "system",
            "content": f"You are a helpful assistant that can get weather information.\n{prompt_template2}"
        },
        {"role": "user", "content": "What's the weather in New York and Tokyo?"}
    ]
    
    # Create a new stream for the second example
    stream2 = await client.chat.completions.create(
        model="deepseek-reasoner",
        messages=messages,
        stream=True,
        stream_options={"include_usage": True}
    )
    
    # Process the second stream
    async for delta, call_info, reasoning_content, usage in stream_parser.parse_stream_output(stream2):
        # Print reasoning content if present
        if reasoning_content:
            print(f"Reasoning: {reasoning_content}")
        
        # Print parsed content (without function calls)
        if delta:
            print(f"Content: {delta.content} (finish reason: {delta.finish_reason})")
        
        # Handle tool calls
        if call_info and isinstance(call_info, AgentCall):
            print(f"\nTool Call:")
            print(f"Instructions: {call_info.instructions}")
            print(f"Agent ID: {call_info.agent_id}")
            print(f"Name: {call_info.name}")
            print(f"Arguments: {json.dumps(call_info.arguments, indent=2)}")

            # A2A tool execution
            messages = Message(
                role=MessageRole.USER,
                content=TextContent(text=json.dumps(call_info.arguments))
            )
            response = a2a_client.send_message(messages)

            # Simulate tool execution
            result_manager.add_agent_result(
                name=call_info.name,
                result=json.loads(response.content.text),
                agent_id=call_info.agent_id
            )
            
        # Print usage statistics if available
        if usage:
            print(f"\nUsage Statistics:")
            print(f"Prompt tokens: {usage.prompt_tokens}")
            print(f"Completion tokens: {usage.completion_tokens}")
            print(f"Total tokens: {usage.total_tokens}")
    
    # Print final results
    print("\nFinal Tool Results:")
    print(result_manager.get_agent_results())

async def example_generate_prompt() -> None:
    """Example of generating prompt templates.
    
    This example shows how to generate different types of prompt templates
    for function calling.
    """
    print("\nExample 1: Generate Prompt Templates")
    print("=" * 50)
    
    # Generate prompt template
    prompt_template1 = AgentPromptGenerator.generate_agent_prompt(functions1)
    
    print("\nGenerated Prompt Template:")
    print("-" * 50)
    print(prompt_template1)
    print("-" * 50)

    # Generate prompt template
    prompt_template2 = AgentPromptGenerator.generate_agent_prompt(functions2)
    
    print("\nGenerated Prompt Template:")
    print("-" * 50)
    print(prompt_template2)
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