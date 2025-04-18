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

To run the example code, you need to install additional dependencies. The examples are located in the `examples` directory, and each example has its specific dependency requirements:

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
content, tool_calls = parser.parse_output(output)
print(f"Content: {content}")
print(f"Function calls: {tool_calls}")
```

### 3. Async Streaming Processing and Function Calling

```python
from mfcs.response_parser import ResponseParser
from mfcs.result_manager import ResultManager

async def process_stream():
    parser = ResponseParser()
    result_manager = ResultManager()
    
    async for chunk in stream:
        content, tool_calls = parser.parse_stream_output(chunk)
        if content:
            print(content, end="", flush=True)
        if tool_calls:
            for tool_call in tool_calls:
                # Process function call and store results
                result = await process_function_call(tool_call)
                result_manager.add_result(tool_call['call_id'], tool_call['name'], result)
    
    # Get all processing results
    return result_manager.get_results()
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

The memory prompt template includes:
- Memory tool usage rules
- Memory tool interface specifications
- Memory usage restrictions
- Memory application strategies

### 5. Result Management System

The Result Management System provides a unified way to handle and format results from both tool calls and memory operations in LLM interactions. It ensures consistent result handling and proper cleanup.

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

# Retrieve specific results by ID
weather_result = result_manager.get_tool_result("weather_1")
memory_result = result_manager.get_memory_result("memory_1")
```

Key Features:
- **Unified Management**: Handles both tool call results and memory operation results
- **Structured Formatting**: Outputs results in a consistent XML-like format for LLM processing
- **Automatic Cleanup**: Results are automatically cleared after retrieval to prevent memory leaks
- **JSON Compatibility**: Supports JSON-serializable results with automatic string conversion
- **ID-based Retrieval**: Allows fetching specific results using unique identifiers
- **Type Safety**: Validates input parameters and handles various result types

The system is designed to:
1. Maintain a clean separation between tool calls and memory operations
2. Ensure consistent result formatting for LLM consumption
3. Prevent memory leaks through automatic cleanup
4. Support both synchronous and asynchronous operations
5. Handle various result types through automatic conversion

## Examples

Check out the `examples` directory for more detailed examples:

- `function_calling_examples.py`: Basic function calling examples
  - Function prompt generation
  - Function call parsing
  - Result management

- `async_function_calling_examples.py`: Async streaming examples
  - Async streaming best practices
  - Concurrent function call handling
  - Async error handling and timeout control

Run the examples to see the library in action:

```bash
# Run basic examples
python examples/function_calling_examples.py

# Run async examples
python examples/async_function_calling_examples.py
```

## Notes

- The library requires Python 3.8+ for async features
- Make sure to handle API keys and sensitive information securely
- For production use, replace simulated API calls with actual implementations
- Follow the tool calling rules in the prompt template
- Use unique call_ids for each function call
- Provide clear instructions for each function call
- Handle errors and resource cleanup in async streaming processing
- Use `ResultManager` to manage results from multiple function calls
- Handle exceptions and timeouts properly in async context
- Use `MemoryPromptManager` for managing conversation context

## System Requirements

- Python 3.8 or higher

## License

MIT License 