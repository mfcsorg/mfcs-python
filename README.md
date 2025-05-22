# MFCS (Model Function Calling Standard)

<div align="right">
  <a href="README.md">English</a> | 
  <a href="README_CN.md">中文</a>
</div>

Model Function Calling Standard

A Python library for handling function calling in Large Language Models (LLMs).

## Features

- Generate standardized function calling prompt templates
- Parse function calls from LLM streaming output
- Validate function schemas
- Async streaming support with real-time processing
- Multiple function call handling
- Memory prompt management
- Result prompt management

## Installation

```bash
pip install mfcs
```

## Configuration

1. Copy `.env.example` to `.env`:
```bash
cp .env.example .env
```

2. Edit `.env` and set your environment variables:
```bash
# OpenAI API Configuration
OPENAI_API_KEY=your-api-key-here
OPENAI_API_BASE=your-api-base-url-here
```

## Example Installation

To run the example code, you need to install additional dependencies. The examples are located in the `examples` directory:

```bash
cd examples
pip install -r requirements.txt
```

## Usage

### 1. Generate Function Calling Prompt Templates

```python
from mfcs.function_prompt import FunctionPromptGenerator

# Define your function schemas
functions = [
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

# Generate prompt template
template = FunctionPromptGenerator.generate_function_prompt(functions)
```

### 2. Parse Function Calls from Output

```python
from mfcs.response_parser import ResponseParser

# Example function call
output = """
I need to check the weather.

<mfcs_call>
<instructions>Getting weather information for New York</instructions>
<call_id>weather_1</call_id>
<name>get_weather</name>
<parameters>
{
  "location": "New York, NY",
  "unit": "fahrenheit"
}
</parameters>
</mfcs_call>
"""

# Parse the function call
parser = ResponseParser()
content, tool_calls, memory_calls = parser.parse_output(output)
print(f"Content: {content}")
print(f"Function calls: {tool_calls}")
```

### 3. Async Streaming Processing

```python
from mfcs.response_parser import ResponseParser
from mfcs.result_manager import ResultManager
import json

async def process_stream():
    parser = ResponseParser()
    result_manager = ResultManager()
    
    async for delta, call_info, reasoning_content, usage in parser.parse_stream_output(stream):
        # Print reasoning content if present
        if reasoning_content:
            print(f"Reasoning: {reasoning_content}")
            
        # Print parsed content
        if delta:
            print(f"Content: {delta.content} (finish reason: {delta.finish_reason})")
            
        # Handle tool calls
        if call_info and isinstance(call_info, ToolCall):
            print(f"\nTool Call:")
            print(f"Instructions: {call_info.instructions}")
            print(f"Call ID: {call_info.call_id}")
            print(f"Name: {call_info.name}")
            print(f"Arguments: {json.dumps(call_info.arguments, indent=2)}")
            
            # Simulate tool execution (in real application, this would call actual tools)
            # Add API result with call_id (now required)
            result_manager.add_tool_result(
                name=call_info.name,
                result={"status": "success", "data": f"Simulated data for {call_info.name}"},
                call_id=call_info.call_id
            )
            
        # Print usage statistics if available
        if usage:
            print(f"Usage: {usage}")
    
    print("\nTool Results:")
    print(result_manager.get_tool_results())
```

### 4. Memory Prompt Management

```python
from mfcs.memory_prompt import MemoryPromptGenerator

# Define memory APIs
memory_apis = [
    {
        "name": "store_preference",
        "description": "Store user preferences and settings",
        "parameters": {
            "type": "object",
            "properties": {
                "preference_type": {
                    "type": "string",
                    "description": "Type of preference to store"
                },
                "value": {
                    "type": "string",
                    "description": "Value of the preference"
                }
            },
            "required": ["preference_type", "value"]
        }
    }
]

# Generate memory prompt template
template = MemoryPromptGenerator.generate_memory_prompt(memory_apis)
```

### 5. Result Management

The Result Management provides a unified way to handle and format results from both tool calls and memory operations.

```python
from mfcs.result_manager import ResultManager

# Initialize result manager
result_manager = ResultManager()

# Store tool call results
result_manager.add_tool_result(
    name="get_weather",           # Tool name
    result={"temperature": 25},   # Tool execution result
    call_id="weather_1"          # Unique identifier for this call
)

# Store memory operation results
result_manager.add_memory_result(
    name="store_preference",      # Memory operation name
    result={"status": "success"}, # Operation result
    memory_id="memory_1"         # Unique identifier for this operation
)

# Get formatted results for LLM consumption
tool_results = result_manager.get_tool_results()
# Output format:
# <tool_result>
# {call_id: weather_1, name: get_weather} {"temperature": 25}
# </tool_result>

memory_results = result_manager.get_memory_results()
# Output format:
# <memory_result>
# {memory_id: memory_1, name: store_preference} {"status": "success"}
# </memory_result>
```

## Examples

### Function Calling Examples

Demonstrates basic and async function calling with MFCS.

To run the basic example:
```bash
python examples/function_calling_examples.py
```
To run the async example:
```bash
python examples/async_function_calling_examples.py
```

### Memory Function Examples

Demonstrates memory prompt usage and async memory functions.

To run the memory example:
```bash
python examples/memory_function_examples.py
```
To run the async memory example:
```bash
python examples/async_memory_function_examples.py
```

### A2A (Agent-to-Agent) Communication Examples

Demonstrates how to use MFCS for agent-to-agent communication.

To run the server example:
```bash
python examples/a2a_server_example.py
```
To run the async client example:
```bash
python examples/async_a2a_client_example.py
```

### MCP Client Examples

Demonstrates MCP client usage (sync and async).

To run the MCP client example:
```bash
python examples/mcp_client_example.py
```
To run the async MCP client example:
```bash
python examples/async_mcp_client_example.py
```

## Notes

- Async features require Python 3.8+
- Make sure to handle API keys and sensitive information securely
- Replace simulated API calls with actual implementations in production
- Follow the tool call rules in the prompt templates
- Use a unique `call_id` for each function call
- Provide clear instructions for each function call
- Pay attention to error handling and resource cleanup in async streaming
- Use `ResultManager` to manage results from multiple function calls
- Handle exceptions and timeouts properly in async contexts
- Use `MemoryPromptManager` to manage conversation context

## System Requirements

- Python 3.8 or higher

## License

MIT License