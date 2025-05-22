# MFCS (模型函数调用标准)

<div align="right">
  <a href="README.md">English</a> | 
  <a href="README_CN.md">中文</a>
</div>

模型函数调用标准

一个用于处理大语言模型（LLM）函数调用的 Python 库。

## 特性

- 支持函数、记忆、Agent 多类型调用的标准化管理
- 生成标准化的函数、记忆、Agent 调用提示模板
- 解析 LLM 输出中的函数、记忆、Agent 调用（支持同步与异步流式处理）
- 验证函数、记忆、Agent 调用的参数和模式
- 多调用类型的统一结果管理与格式化输出
- 支持异步流式处理，实时解析和处理多类型调用
- 便捷的调用唯一标识与调用追踪
- 适用于多智能体（Agent）协作、工具调用、记忆管理等多场景
- 易于扩展和集成，适配多种 LLM 应用需求

## 安装

```bash
pip install mfcs
```

## 配置

1. 复制 `.env.example` 到 `.env`:
```bash
cp .env.example .env
```

2. 编辑 `.env` 并设置您的环境变量:
```bash
# OpenAI API Configuration
OPENAI_API_KEY=your-api-key-here
OPENAI_API_BASE=your-api-base-url-here
```

## 示例安装

要运行示例代码，需要安装额外的依赖。示例代码位于 `examples` 目录：

```bash
cd examples
pip install -r requirements.txt
```

## 示例说明

`examples` 目录包含：
- **函数调用示例**：  
  - `function_calling_examples.py`  
    展示 MFCS 的基础函数调用。
  - `async_function_calling_examples.py`  
    展示异步函数调用。
- **记忆函数示例**：  
  - `memory_function_examples.py`  
    展示记忆提示的用法。
  - `async_memory_function_examples.py`  
    记忆函数的异步用法。
- **A2A（Agent-to-Agent）通信示例**：  
  - `a2a_server_example.py`  
    智能体通信服务端示例。
  - `async_a2a_client_example.py`  
    智能体通信异步客户端示例。
- **MCP 客户端示例**：  
  - `mcp_client_example.py`, `async_mcp_client_example.py`  
    展示 MCP 客户端的用法。

## 使用方法

## 1. 生成提示模板

### 1.1 生成函数调用提示模板

```python
from mfcs.function_prompt import FunctionPromptGenerator

# 定义函数模式
functions = [
    {
        "name": "get_weather",
        "description": "获取指定位置的天气信息",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "城市和州，例如：San Francisco, CA"
                },
                "unit": {
                    "type": "string",
                    "enum": ["celsius", "fahrenheit"],
                    "description": "温度单位",
                    "default": "celsius"
                }
            },
            "required": ["location"]
        }
    }
]

# 生成提示模板
template = FunctionPromptGenerator.generate_function_prompt(functions)
```

### 1.2 生成记忆提示模板

```python
from mfcs.memory_prompt import MemoryPromptGenerator

# 定义记忆 API
memory_apis = [
    {
        "name": "store_preference",
        "description": "存储用户偏好和设置",
        "parameters": {
            "type": "object",
            "properties": {
                "preference_type": {
                    "type": "string",
                    "description": "要存储的偏好类型"
                },
                "value": {
                    "type": "string",
                    "description": "偏好的值"
                }
            },
            "required": ["preference_type", "value"]
        }
    }
]

# 生成记忆提示模板
template = MemoryPromptGenerator.generate_memory_prompt(memory_apis)
```

### 1.3 生成 Agent 提示模板

```python
from mfcs.agent_prompt import AgentPromptGenerator

# 定义 agent API
agent_apis = [
    {
        "name": "send_result",
        "description": "将结果发送给指定的 agent",
        "parameters": {
            "type": "object",
            "properties": {
                "content": {
                    "type": "string",
                    "description": "需要发送的内容"
                }
            },
            "required": ["content"]
        }
    }
]

# 生成 agent 提示模板
template = AgentPromptGenerator.generate_agent_prompt(agent_apis)
```

## 2. 解析与调用

### 2.1 解析输出中的函数、记忆、Agent 调用

```python
from mfcs.response_parser import ResponseParser

# 函数调用示例
output = """
我需要查询天气信息，并保存我的偏好，同时让 agent_A 处理结果。

<mfcs_call>
<instructions>获取纽约的天气信息</instructions>
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
<instructions>保存用户偏好</instructions>
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
<instructions>将天气结果发送给 agent_B</instructions>
<agent_id>agent_1</agent_id>
<name>send_result</name>
<parameters>
{
  "content": "纽约天气为 25°F，已发送给 agent_B"
}
</parameters>
</mfcs_agent>
"""

parser = ResponseParser()
content, tool_calls, memory_calls, agent_calls = parser.parse_output(output)
print(f"内容: {content}")
print(f"函数调用: {tool_calls}")
print(f"记忆调用: {memory_calls}")
print(f"Agent 调用: {agent_calls}")

# 说明：
# output 现在包含 <mfcs_call>、<mfcs_memory> 和 <mfcs_agent> 三种标签。
# <mfcs_agent> 的 <parameters> 只包含 content 字段。
# parse_output 返回 agent_calls，便于后续处理 agent 相关逻辑。
```

### 2.2 异步流式处理函数、记忆、Agent 调用

```python
from mfcs.response_parser import ResponseParser, ToolCall, MemoryCall, AgentCall
from mfcs.result_manager import ResultManager
import json

async def process_stream():
    parser = ResponseParser()
    result_manager = ResultManager()
    
    async for delta, call_info, reasoning_content, usage, memory_info, agent_info in parser.parse_stream_output(stream):
        # 打印推理内容（如果有）
        if reasoning_content:
            print(f"推理: {reasoning_content}")
        
        # 打印解析后的内容
        if delta:
            print(f"内容: {delta.content} (完成原因: {delta.finish_reason})")
        
        # 处理工具调用
        if call_info and isinstance(call_info, ToolCall):
            print(f"\n工具调用:")
            print(f"指令: {call_info.instructions}")
            print(f"调用ID: {call_info.call_id}")
            print(f"名称: {call_info.name}")
            print(f"参数: {json.dumps(call_info.arguments, indent=2)}")
            # 模拟工具执行
            result_manager.add_tool_result(
                name=call_info.name,
                result={"status": "success", "data": f"模拟数据 for {call_info.name}"},
                call_id=call_info.call_id
            )
        
        # 处理记忆调用
        if memory_info and isinstance(memory_info, MemoryCall):
            print(f"\n记忆调用:")
            print(f"指令: {memory_info.instructions}")
            print(f"记忆ID: {memory_info.memory_id}")
            print(f"名称: {memory_info.name}")
            print(f"参数: {json.dumps(memory_info.arguments, indent=2)}")
            # 模拟记忆操作
            result_manager.add_memory_result(
                name=memory_info.name,
                result={"status": "success"},
                memory_id=memory_info.memory_id
            )
        
        # 处理 agent 调用
        if agent_info and isinstance(agent_info, AgentCall):
            print(f"\nAgent 调用:")
            print(f"指令: {agent_info.instructions}")
            print(f"Agent ID: {agent_info.agent_id}")
            print(f"名称: {agent_info.name}")
            print(f"参数: {json.dumps(agent_info.arguments, indent=2)}")
            # 模拟 Agent 操作
            result_manager.add_agent_result(
                name=agent_info.name,
                result={"status": "success"},
                memory_id=agent_info.agent_id
            )
        
        # 打印使用统计（如果有）
        if usage:
            print(f"使用统计: {usage}")
    
    print("\n工具调用结果:")
    print(result_manager.get_tool_results())
    print("记忆调用结果:")
    print(result_manager.get_memory_results())
    print("Agent 调用结果:")
    print(result_manager.get_agent_results())
```

## 3. 结果管理

### 3.1 函数、记忆、Agent 执行结果管理

结果管理提供了一种统一的方式来处理和格式化 LLM 交互中的工具调用、记忆操作和 Agent 操作结果。它确保结果处理的一致性和适当的清理机制。

```python
from mfcs.result_manager import ResultManager

# 初始化结果管理器
result_manager = ResultManager()

# 存储工具调用结果
result_manager.add_tool_result(
    name="get_weather",           # 工具名称
    result={"temperature": 25},   # 工具执行结果
    call_id="weather_1"          # 调用的唯一标识符
)

# 存储记忆操作结果
result_manager.add_memory_result(
    name="store_preference",      # 记忆操作名称
    result={"status": "success"}, # 操作结果
    memory_id="memory_1"         # 操作的唯一标识符
)

# 存储 agent 操作结果
result_manager.add_agent_result(
    name="send_result",                # Agent 操作名称
    result={"status": "success"},      # 操作结果
    agent_id="agent_1"                 # 操作的唯一标识符
)

# 获取格式化结果供 LLM 使用
tool_results = result_manager.get_tool_results()
# 输出格式：
# <tool_result>
# {call_id: weather_1, name: get_weather} {"temperature": 25}
# </tool_result>

memory_results = result_manager.get_memory_results()
# 输出格式：
# <memory_result>
# {memory_id: memory_1, name: store_preference} {"status": "success"}
# </memory_result>

agent_results = result_manager.get_agent_results()
# 输出格式：
# <agent_result>
# {agent_id: agent_1, name: send_result} {"status": "success"}
# </agent_result>
```

## 示例

### 函数调用示例

展示 MFCS 的基础和异步函数调用。

运行基础示例：
```bash
python examples/function_calling_examples.py
```
运行异步示例：
```bash
python examples/async_function_calling_examples.py
```

### 记忆函数示例

展示记忆提示用法和异步记忆函数。

运行记忆示例：
```bash
python examples/memory_function_examples.py
```
运行异步记忆示例：
```bash
python examples/async_memory_function_examples.py
```

### A2A（Agent-to-Agent）通信示例

展示如何使用 MFCS 实现智能体间通信。

运行服务端：
```bash
python examples/a2a_server_example.py
```
运行异步客户端：
```bash
python examples/async_a2a_client_example.py
```

### MCP 客户端示例

展示 MCP 客户端（同步与异步）用法。

运行 MCP 客户端示例：
```bash
python examples/mcp_client_example.py
```
运行异步 MCP 客户端示例：
```bash
python examples/async_mcp_client_example.py
```

## 注意事项

- **Python 版本要求**  
  异步功能需要 Python 3.8 及以上版本。

- **安全性**  
  请确保安全处理 API 密钥和敏感信息，避免泄露。

- **API 调用实现**  
  示例代码中的 API 调用为模拟实现，生产环境请替换为实际业务逻辑。

- **调用唯一标识**  
  - 每个函数调用请使用唯一的 `call_id`。
  - 每个记忆操作请使用唯一的 `memory_id`。
  - 每个 agent 操作请使用唯一的 `agent_id`。

- **调用格式规范**  
  - `<mfcs_call>`、`<mfcs_memory>`、`<mfcs_agent>` 标签的 `<parameters>` 字段应为标准 JSON 格式。
  - `<mfcs_agent>` 的 `<parameters>` 字段建议仅包含 `content` 字段，保持格式统一。

- **提示模板与调用规则**  
  - 按照各自的 Prompt 生成器生成标准提示模板。
  - 遵循提示模板中的调用规则，确保 LLM 能正确解析和调用。

- **结果管理**  
  - 建议使用 `ResultManager` 统一管理函数、记忆、Agent 的调用结果，便于 LLM 消费和后续处理。
  - 获取结果时请使用对应的 `get_tool_results()`、`get_memory_results()`、`get_agent_results()` 方法。

- **异常与资源管理**  
  - 异步流式处理时注意异常捕获和资源释放，防止内存泄漏或死锁。
  - Agent、函数、记忆调用的异常处理和资源清理建议保持一致。

- **扩展性**  
  如需扩展更多类型的调用或结果管理，可参考现有结构进行自定义。

## 系统要求

- Python 3.8 及以上版本
- 推荐使用最新版 pip 进行依赖安装
- 支持主流操作系统（Windows、Linux、macOS）
- 依赖库详见 requirements.txt

## 许可证

MIT 许可证 