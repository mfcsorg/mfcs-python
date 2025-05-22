# MFCS (Model Function Calling Standard)

<div align="right">
  <a href="README.md">English</a> | 
  <a href="README_CN.md">中文</a>
</div>

Model Function Calling Standard

A Python library for handling function calling in Large Language Models (LLMs).

## Features

- Standardized management for function, memory, and agent calls
- Generate standardized prompt templates for function, memory, and agent calls
- Parse function, memory, and agent calls from LLM output (supports both sync and async streaming)
- Validate parameters and schemas for function, memory, and agent calls
- Unified result management and formatted output for multiple call types
- Async streaming support with real-time multi-type call processing
- Easy unique identifier assignment and call tracking
- Suitable for multi-agent collaboration, tool invocation, memory management, and more
- Highly extensible and integrable for various LLM application scenarios

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

## 1. Prompt Template Generation

### 1.1 Generate Function Calling Prompt Templates

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

### 1.2 Memory Prompt Management

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

### 1.3 Agent Prompt Management

```python
from mfcs.agent_prompt import AgentPromptGenerator

# Define agent APIs
agent_apis = [
    {
        "name": "send_result",
        "description": "Send result to a specified agent",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "The content to send"
                }
            },
            "required": ["content"]
        }
    }
]

# Generate agent prompt template
template = AgentPromptGenerator.generate_agent_prompt(agent_apis)
```

## 2. Parsing and Invocation

### 2.1 Parse Function, Memory, and Agent Calls from Output

```python
from mfcs.response_parser import ResponseParser

output = """
I need to check the weather and save my preference, and also let agent_A handle the result.

<mfcs_call>
<instructions>Get the weather information for New York</instructions>
<call_id>weather_1</call_id>
<name>get_weather</name>
<parameters>
{
  "location": "New York, NY",
  "unit": "fahrenheit"
}
</parameters>
</mfcs_call>

<mfcs_memory>
<instructions>Save user preference</instructions>
<memory_id>memory_1</memory_id>
<name>store_preference</name>
<parameters>
{
  "preference_type": "weather_unit",
  "value": "fahrenheit"
}
</parameters>
</mfcs_memory>

<mfcs_agent>
<instructions>Send the weather result to agent_B</instructions>
<agent_id>agent_1</agent_id>
<name>send_result</name>
<parameters>
{
  "content": "The weather in New York is 25°F, sent to agent_B."
}
</parameters>
</mfcs_agent>
"""

parser = ResponseParser()
content, tool_calls, memory_calls, agent_calls = parser.parse_output(output)
print(f"Content: {content}")
print(f"Function calls: {tool_calls}")
print(f"Memory calls: {memory_calls}")
print(f"Agent calls: {agent_calls}")

# Explanation:
# The output now includes <mfcs_call>, <mfcs_memory>, and <mfcs_agent> blocks.
# The <mfcs_agent> block's <parameters> only contains a 'content' field.
# The parser returns agent_calls for further agent-related processing.
```

### 2.2 Async Streaming Processing for Function, Memory, and Agent Calls

```python
from mfcs.response_parser import ResponseParser, ToolCall, MemoryCall, AgentCall
from mfcs.result_manager import ResultManager
import json

async def process_stream():
    parser = ResponseParser()
    result_manager = ResultManager()
    
    async for delta, call_info, reasoning_content, usage, memory_info, agent_info in parser.parse_stream_output(stream):
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
            # Simulate tool execution
            result_manager.add_tool_result(
                name=call_info.name,
                result={"status": "success", "data": f"Simulated data for {call_info.name}"},
                call_id=call_info.call_id
            )

        # Handle memory calls
        if memory_info and isinstance(memory_info, MemoryCall):
            print(f"\nMemory Call:")
            print(f"Instructions: {memory_info.instructions}")
            print(f"Memory ID: {memory_info.memory_id}")
            print(f"Name: {memory_info.name}")
            print(f"Arguments: {json.dumps(memory_info.arguments, indent=2)}")
            # Simulate memory operation
            result_manager.add_memory_result(
                name=memory_info.name,
                result={"status": "success"},
                memory_id=memory_info.memory_id
            )

        # Handle agent calls
        if agent_info and isinstance(agent_info, AgentCall):
            print(f"\nAgent Call:")
            print(f"Instructions: {agent_info.instructions}")
            print(f"Agent ID: {agent_info.agent_id}")
            print(f"Name: {agent_info.name}")
            print(f"Arguments: {json.dumps(agent_info.arguments, indent=2)}")
            # Simulate Agent operation
            result_manager.add_agent_result(
                name=agent_info.name,
                result={"status": "success"},
                memory_id=agent_info.agent_id
            )

        # Print usage statistics if available
        if usage:
            print(f"Usage: {usage}")

    print("\nTool Results:")
    print(result_manager.get_tool_results())
    print("Memory Results:")
    print(result_manager.get_memory_results())
    print("Agent Results:")
    print(result_manager.get_agent_results())
```

## 3. Result Management

### 3.1 Function, Memory, and Agent Result Management

The Result Management provides a unified way to handle and format results from tool calls, memory operations, and agent operations in LLM interactions. It ensures consistency and proper cleanup.

```python
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

# Store agent operation results
result_manager.add_agent_result(
    name="send_result",                # Agent operation name
    result={"status": "success"},      # Operation result
    agent_id="agent_1"                 # Unique identifier for this operation
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

agent_results = result_manager.get_agent_results()
# Output format:
# <agent_result>
# {agent_id: agent_1, name: send_result} {"status": "success"}
# </agent_result>
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

- **Python Version Requirement**  
  Async features require Python 3.8 or higher.

- **Security**  
  Make sure to handle API keys and sensitive information securely to avoid leaks.

- **API Call Implementation**  
  The API calls in the example code are simulated. Replace them with your actual business logic in production.

- **Unique Identifiers**  
  - Use a unique `call_id` for each function call.
  - Use a unique `memory_id` for each memory operation.
  - Use a unique `agent_id` for each agent operation.

- **Call Format Specification**  
  - The `<mfcs_call>`, `<mfcs_memory>`, and `<mfcs_agent>` blocks' `<parameters>` fields should be standard JSON.
  - The `<mfcs_agent>` block's `<parameters>` should only contain a `content` field for consistency.

- **Prompt Template and Call Rules**  
  - Always generate prompt templates using the appropriate prompt generator.
  - Follow the call rules in the prompt templates to ensure the LLM can parse and invoke correctly.

- **Result Management**  
  - Use `ResultManager` to manage results from function, memory, and agent calls for unified LLM consumption and post-processing.
  - Use `get_tool_results()`, `get_memory_results()`, and `get_agent_results()` to retrieve results.

- **Error and Resource Management**  
  - Pay attention to exception handling and resource cleanup in async streaming to prevent memory leaks or deadlocks.
  - Keep error handling and resource cleanup consistent across agent, function, and memory calls.

- **Extensibility**  
  If you need to support more types of calls or result management, you can extend the current structure as a reference.

## System Requirements

- Python 3.8 or higher
- Latest pip recommended for dependency installation
- Compatible with major operating systems (Windows, Linux, macOS)
- See requirements.txt for dependencies

## License

MIT License