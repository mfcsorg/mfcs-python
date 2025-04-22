# Node.js server implements Model Context Protocol (MCP) for file system operations

# ClientSession represents the client session for interacting with the server
# StdioServerParameters defines the stdio connection parameters with the server
import json
from dotenv import load_dotenv
from mcp import ClientSession, StdioServerParameters
# Provides stdio connection context manager with the server
from mcp.client.stdio import stdio_client
import asyncio
import os
from openai import AsyncOpenAI
from mfcs.function_prompt import FunctionPromptGenerator
from mfcs.response_parser import MemoryCall, ResponseParser, ToolCall
from mfcs.result_manager import ResultManager


# Load environment variables
load_dotenv()

# Configure OpenAI
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_BASE"))


# Create server parameters for stdio connection
server_params = StdioServerParameters(
    # Server execution command, here it's npx
    command="npx",
    # Additional parameters for the startup command, here running server-filesystem
    args=["@modelcontextprotocol/server-filesystem", "./"],
    # Environment variables, default is None, meaning use current environment variables
    env=None
)


async def run():
    print("Starting client...")
    
    # Create stdio connection with the server
    async with stdio_client(server_params) as (read, write):
        print("Connected to server...")
        
        # Create a client session object
        async with ClientSession(read, write) as session:
            # Initialize the session
            capabilities = await session.initialize()
            print("Server initialized...")

            # Request server to list all supported tools
            tools = await session.list_tools()
            
            # Convert tools to structured JSON format
            tools_functions = []
            for tool in tools.tools:
                tools_functions.append({
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.inputSchema
                })

            # Generate function calling prompt
            function_prompt = FunctionPromptGenerator.generate_function_prompt(tools_functions)
            print("\nGenerated function prompt:")
            print(function_prompt)

            # Create chat completion request with streaming
            print("\nChat completion response (streaming):")
            stream = await client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[
                    {"role": "system", "content": function_prompt},
                    {"role": "user", "content": "What is 1+1 equal to? Please use the list_directory function to list all files in the examples directory. Make sure to call the list_directory function with the appropriate parameters. Please explain in detail."}
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
                if call_info and isinstance(call_info, ToolCall):
                    print(f"\nTool Call:")
                    print(f"Instructions: {call_info.instructions}")
                    print(f"Call ID: {call_info.call_id}")
                    print(f"Name: {call_info.name}")
                    print(f"Arguments: {json.dumps(call_info.arguments, indent=2)}")
                    
                    # Execute the actual tool call
                    result = await session.call_tool(call_info.name, arguments=call_info.arguments)

                    # Add tool result
                    result_manager.add_tool_result(
                        name=call_info.name,
                        result=result.content,
                        call_id=call_info.call_id
                    )
                
                # Handle memory calls
                if call_info and isinstance(call_info, MemoryCall):
                    print(f"\nMemory Call:")
                    print(f"Instructions: {call_info.instructions}")
                    print(f"Memory ID: {call_info.memory_id}")
                    print(f"Name: {call_info.name}")
                    print(f"Arguments: {json.dumps(call_info.arguments, indent=2)}")

                    # Execute the actual tool call
                    result = await session.call_tool(call_info.name, arguments=call_info.arguments)

                    # Add tool result
                    result_manager.add_memory_result(
                        name=call_info.name,
                        result=result.content,
                        memory_id=call_info.memory_id
                    )
                
                # Print usage statistics if available
                if usage:
                    print(f"\nUsage Statistics:")
                    print(f"Prompt tokens: {usage.prompt_tokens}")
                    print(f"Completion tokens: {usage.completion_tokens}")
                    print(f"Total tokens: {usage.total_tokens}")
            
            # Print results
            print("\nTool Results:")
            print(result_manager.get_tool_results())

            # Print results
            print("\nMemory Results:")
            print(result_manager.get_memory_results())


if __name__ == "__main__":
    asyncio.run(run())