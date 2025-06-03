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
from mfcs.response_parser import ResponseParser
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

            # Create chat completion request (non-streaming)
            print("\nSending chat completion request...")
            response = await client.chat.completions.create(
                model="deepseek-reasoner",
                messages=[
                    {"role": "system", "content": function_prompt},
                    {"role": "user", "content": "Please use the list_directory function to list all files in the examples directory. Make sure to call the list_directory function with the appropriate parameters."}
                ]
            )
            
            # Initialize result handler
            result_manager = ResultManager()
            
            print("\nResponse:")
            print("-" * 30)
            
            # Get the response content
            content = response.choices[0].message.content
            print(f"Content: {content}")
            
            # Parse the function calls using ResponseParser
            response_parser = ResponseParser()
            content, tool_calls, memory_calls, agent_calls = response_parser.parse_output(content)

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
            
            print("\nTool Calls:")
            if tool_calls:
                for tool_call in tool_calls:
                    print(f"Function: {tool_call.name}")
                    print(f"Arguments: {json.dumps(tool_call.arguments, indent=2)}")
                
                # Execute the actual tool call
                result = await session.call_tool(tool_call.name, arguments=tool_call.arguments)

                # Add tool result
                result_manager.add_tool_result(
                    name=tool_call.name,
                    result=result.content,
                    call_id=tool_call.call_id
                )

            # Print results
            print("\nTool Results:")
            print(result_manager.get_tool_results())

            print("\nMemory Calls:")
            if memory_calls:
                for memory_call in memory_calls:
                    print(f"Function: {memory_call.name}")
                    print(f"Arguments: {json.dumps(memory_call.arguments, indent=2)}")
                
                # Execute the actual memory call
                result = await session.call_tool(memory_call.name, arguments=memory_call.arguments)

                # Add memory result
                result_manager.add_memory_result(
                    name=memory_call.name,
                    result=result.content,
                    memory_id=memory_call.memory_id
                )

            # Print results
            print("\nMemory Results:")
            print(result_manager.get_memory_results())

            print("\nAgent Calls:")
            if agent_calls:
                for agent_call in agent_calls:
                    print(f"Function: {agent_call.name}")
                    print(f"Arguments: {json.dumps(agent_call.arguments, indent=2)}")

            # Print results
            print("\nAgent Results:")
            print(result_manager.get_agent_results())


if __name__ == "__main__":
    asyncio.run(run())