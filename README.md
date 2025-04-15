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

To run the example code, you need to install additional dependencies. The examples are located in the `examples` directory, and each example has its specific dependency requirements:

```bash
cd examples
pip install -r requirements.txt
```

## Usage

### 1. Generate Function Calling Prompt Templates

```python
from mfcs.function_calling.function_prompt import FunctionPromptGenerator

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
from mfcs.function_calling.response_parser import ResponseParser

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
content, tool_calls = parser.parse_output(output)
print(f"Content: {content}")
print(f"Function calls: {tool_calls}")
```

### 3. Async Streaming Processing and Function Calling

```python
from mfcs.function_calling.response_parser import ResponseParser
from mfcs.function_calling.api_result_manager import ApiResultManager

async def process_stream():
    parser = ResponseParser()
    api_results = ApiResultManager()
    
    async for chunk in stream:
        content, tool_calls = parser.parse_stream_output(chunk)
        if content:
            print(content, end="", flush=True)
        if tool_calls:
            for tool_call in tool_calls:
                # Process function call and store results
                result = await process_function_call(tool_call)
                api_results.add_api_result(tool_call['call_id'], tool_call['name'], result)
    
    # Get all processing results
    return api_results.get_api_results()
```

## Examples

Check out the `examples` directory for more detailed examples:

- `function_calling_examples.py`: Basic function calling examples
  - Function prompt generation
  - Function call parsing
  - API result management

- `async_function_calling_examples.py`: Async streaming examples
  - Async streaming best practices
  - Concurrent function call handling
  - Async error handling and timeout control

- `mcp_client_example.py`: MCP client integration examples
  - Basic MCP client setup
  - Function registration
  - Tool calling implementation

- `async_mcp_client_example.py`: Async MCP client examples
  - Async MCP client configuration
  - Async tool calling implementation
  - Concurrent task processing

Run the examples to see the library in action:

```bash
# Run basic examples
python examples/function_calling_examples.py
python examples/mcp_client_example.py

# Run async examples
python examples/async_function_calling_examples.py
python examples/async_mcp_client_example.py
```

## Notes

- The library requires Python 3.8+ for async features
- Make sure to handle API keys and sensitive information securely
- For production use, replace simulated API calls with actual implementations
- Follow the tool calling rules in the prompt template
- Use unique call_ids for each function call
- Provide clear instructions for each function call
- Handle errors and resource cleanup in async streaming processing
- Use `ApiResultManager` to manage results from multiple function calls
- Handle exceptions and timeouts properly in async context

## System Requirements

- Python 3.8 or higher

## License

MIT License 