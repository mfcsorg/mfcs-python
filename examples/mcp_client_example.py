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
from mfcs.function_calling.function_prompt import FunctionPromptGenerator
from openai import AsyncOpenAI
from mfcs.function_calling.response_parser import ResponseParser
from mfcs.function_calling.api_result_manager import ApiResultManager


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
                model="qwen-plus-latest",
                messages=[
                    {"role": "system", "content": function_prompt},
                    {"role": "user", "content": "Please use the list_directory function to list all files in the examples directory. Make sure to call the list_directory function with the appropriate parameters."}
                ]
            )
            
            # Initialize result handler
            api_result_manager = ApiResultManager()
            
            print("\nResponse:")
            print("-" * 30)
            
            # Get the response content
            content = response.choices[0].message.content
            print(f"Content: {content}")
            
            # Parse the function calls using ResponseParser
            parser = ResponseParser()
            parsed_content, tool_calls = parser.parse_output(content)
            
            print("\nParsed Content:")
            print(parsed_content)
            
            print("\nParsed Tool Calls:")
            for tool_call in tool_calls:
                print(f"Function: {tool_call['name']}")
                print(f"Arguments: {json.dumps(tool_call['arguments'], indent=2)}")
                
                # Execute the actual tool call
                result = await session.call_tool(tool_call['name'], arguments=tool_call['arguments'])

                # Add API result
                api_result_manager.add_api_result(
                    call_id=tool_call.get('call_id', 'unknown'),
                    result=result.content,
                    name=tool_call['name']
                )
            
            # Print results
            print("\nAPI Results:")
            print(api_result_manager.get_api_results())


if __name__ == "__main__":
    asyncio.run(run())