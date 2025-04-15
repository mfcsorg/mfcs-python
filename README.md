# MFCS (Model Function Calling Standard)

<div align="right">
  <a href="README.md">English</a> | 
  <a href="README_CN.md">中文</a>
</div>

Model Function Calling Standard

A Python library for handling function calling in Large Language Models (LLMs).

## Features

- Generate function calling prompt templates
- Parse function calls from LLM streaming output
- Validate function schemas
- Async streaming support
- API result management
- Multiple function call handling

## Installation

```bash
pip install -e .
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

## Usage

### 1. Generate Function Calling Prompt Templates

```python
from mfcs.function_calling import FunctionCallingPromptGenerator

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
template = FunctionCallingPromptGenerator.generate_function_prompt(functions)
```

### 2. Parse Function Calls from Output

```python
from mfcs.function_calling import StreamParser

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
parser = StreamParser()
content, tool_calls = parser.parse_output(output)
print(f"Content: {content}")
print(f"Function calls: {tool_calls}")
```

### 3. Process Streaming Output

```python
from mfcs.function_calling import StreamParser

# Process streaming output
parser = StreamParser()

# In a streaming loop
for chunk in stream:
    content, tool_calls = parser.parse_stream_output(chunk)
    if content:
        print(content, end="", flush=True)
    if tool_calls:
        for tool_call in tool_calls:
            print(f"Function {tool_call['name']} called with arguments: {tool_call['arguments']}")
```

### 4. Async Streaming with Function Calling

```python
from mfcs.function_calling import StreamParser, ApiResultManager
import asyncio

async def process_stream():
    parser = StreamParser()
    api_results = ApiResultManager()
    
    async for chunk in stream:
        content, tool_calls = parser.parse_stream_output(chunk)
        if content:
            print(content, end="", flush=True)
        if tool_calls:
            for tool_call in tool_calls:
                # Process the function call
                result = await process_function_call(tool_call)
                # Add the result
                api_results.add_result(tool_call['call_id'], tool_call['name'], result)
    
    # Get all results
    results = api_results.get_api_results()
```

## Examples

Check out the `examples` directory for more detailed examples:

- `function_calling_examples.py`: Basic function calling examples
  - Function prompt generation
  - Stream parsing
  - Multiple function calls handling
  - API result management

- `async_function_calling_examples.py`: Async streaming examples
  - Async stream processing
  - Concurrent function calls
  - Error handling in async context

- `mcp_client_example.py`: MCP client integration examples
  - Basic MCP client setup
  - Function registration
  - Tool calling implementation

- `async_mcp_client_example.py`: Async MCP client examples
  - Async MCP client setup
  - Concurrent tool execution
  - Async result handling

Each example file includes detailed comments and demonstrates different aspects of the library's functionality. Run the examples to see the library in action:

```bash
# Run basic examples
python examples/function_calling_examples.py
python examples/mcp_client_example.py

# Run async examples
python examples/async_function_calling_examples.py
python examples/async_mcp_client_example.py
```

## Notes

- The library requires Python 3.7+ for async features
- Make sure to handle API keys and sensitive information securely
- For production use, replace simulated API calls with actual implementations
- Follow the tool calling rules in the prompt template
- Use unique call_ids for each function call
- Provide clear instructions for each function call

## License

MIT License 