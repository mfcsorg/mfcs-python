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
    args=["@modelcontextprotocol/server-filesystem", os.path.dirname(__file__)],
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
                model="qwen-plus-latest",
                messages=[
                    {"role": "system", "content": function_prompt},
                    {"role": "user", "content": "Please use the list_directory function to list all files in the examples directory. Make sure to call the list_directory function with the appropriate parameters."}
                ],
                stream=True
            )
            
            # Initialize stream parser and result handler
            stream_parser = ResponseParser()
            result_manager = ResultManager()
            
            print("\nStreaming Response:")
            print("-" * 30)
            
            # Process the stream in real-time
            async for content, tool_call in stream_parser.parse_stream_output(stream):
                # Print parsed content (without function calls)
                if content:
                    print(f"Content: {content}")
                
                # Handle tool calls
                if tool_call and isinstance(tool_call, ToolCall):
                    print(f"\nTool Call:")
                    print(f"Instructions: {tool_call.instructions}")
                    print(f"Call ID: {tool_call.call_id}")
                    print(f"Name: {tool_call.name}")
                    print(f"Arguments: {json.dumps(tool_call.arguments, indent=2)}")
                    
                    # Execute the actual tool call
                    result = await session.call_tool(tool_call.name, arguments=tool_call.arguments)

                    # Add tool result
                    result_manager.add_tool_result(
                        call_id=tool_call.call_id,
                        result=result.content,
                        name=tool_call.name
                    )
                
                # Handle memory calls
                if tool_call and isinstance(tool_call, MemoryCall):
                    print(f"\nMemory Call:")
                    print(f"Instructions: {tool_call.instructions}")
                    print(f"Memory ID: {tool_call.memory_id}")
                    print(f"Name: {tool_call.name}")
                    print(f"Arguments: {json.dumps(tool_call.arguments, indent=2)}")

                    # Execute the actual tool call
                    result = await session.call_tool(tool_call.name, arguments=tool_call.arguments)

                    # Add tool result
                    result_manager.add_memory_result(
                        memory_id=tool_call.memory_id,
                        result=result.content,
                        name=tool_call.name
                    )
            
            # Print results
            print("\nTool Results:")
            print(result_manager.get_tool_results())

            # Print results
            print("\nMemory Results:")
            print(result_manager.get_memory_results())


if __name__ == "__main__":
    asyncio.run(run())