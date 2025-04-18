# MFCS (模型函数调用标准)

<div align="right">
  <a href="README.md">English</a> | 
  <a href="README_CN.md">中文</a>
</div>

模型函数调用标准

一个用于处理大语言模型（LLM）函数调用的 Python 库。

## 特性

- 生成函数调用提示模板
- 解析 LLM 流式输出中的函数调用
- 验证函数模式
- 支持异步流式处理
- 多函数调用处理
- 记忆提示管理
- 结果提示管理

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

要运行示例代码，需要安装额外的依赖。示例代码位于 `examples` 目录，每个示例都有其特定的依赖要求：

```bash
cd examples
pip install -r requirements.txt
```

## 使用方法

### 1. 生成函数调用提示模板

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

### 2. 解析输出中的函数调用

```python
from mfcs.response_parser import ResponseParser

# 函数调用示例
output = """
我需要查询天气信息。

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
"""

# 解析函数调用
parser = ResponseParser()
content, tool_calls = parser.parse_output(output)
print(f"内容: {content}")
print(f"函数调用: {tool_calls}")
```

### 3. 异步流式处理与函数调用

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
                # 处理函数调用并存储结果
                result = await process_function_call(tool_call)
                result_manager.add_result(tool_call['call_id'], tool_call['name'], result)
    
    # 获取所有处理结果
    return result_manager.get_results()
```

### 4. 记忆提示管理

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

记忆提示模板包含：
- 记忆工具使用规则
- 记忆工具接口规范
- 记忆使用限制
- 记忆应用策略

### 5. 结果管理系统

结果管理系统提供了一种统一的方式来处理和格式化 LLM 交互中的工具调用和记忆操作结果。它确保结果处理的一致性和适当的清理机制。

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

# 通过 ID 获取特定结果
weather_result = result_manager.get_tool_result("weather_1")
memory_result = result_manager.get_memory_result("memory_1")
```

主要特性：
- **统一管理**：同时处理工具调用结果和记忆操作结果
- **结构化格式化**：以一致的类 XML 格式输出结果，便于 LLM 处理
- **自动清理**：获取结果后自动清除，防止内存泄漏
- **JSON 兼容**：支持 JSON 可序列化结果，自动进行字符串转换
- **基于 ID 的检索**：支持使用唯一标识符获取特定结果
- **类型安全**：验证输入参数并处理各种结果类型

系统设计目标：
1. 保持工具调用和记忆操作的清晰分离
2. 确保结果格式化的一致性，便于 LLM 使用
3. 通过自动清理防止内存泄漏
4. 支持同步和异步操作
5. 通过自动转换处理各种结果类型

## 示例

查看 `examples` 目录获取更详细的示例：

- `function_calling_examples.py`：基本函数调用示例
  - 函数提示生成
  - 函数调用解析
  - 结果管理

- `async_function_calling_examples.py`：异步流式处理示例
  - 异步流式处理最佳实践
  - 并发函数调用处理
  - 异步错误处理和超时控制

- `mcp_client_example.py`：模型控制协议示例
  - MCP 客户端实现
  - MCP 工具管理
  - MCP 响应处理

- `async_mcp_client_example.py`：异步 MCP 示例
  - 异步 MCP 客户端实现
  - 异步 MCP 工具管理
  - 异步 MCP 响应处理

- `memory_function_examples.py`：记忆函数示例
  - 记忆提示生成
  - 记忆操作
  - 记忆上下文管理

- `async_memory_function_examples.py`：异步记忆示例
  - 异步记忆操作
  - 异步记忆上下文管理
  - 异步记忆持久化

运行示例以查看库的实际效果：

```bash
# 运行基本示例
python function_calling_examples.py

# 运行异步示例
python async_function_calling_examples.py

# 运行 MCP 示例
python mcp_client_example.py

# 运行异步 MCP 示例
python async_mcp_client_example.py

# 运行记忆示例
python memory_function_examples.py

# 运行异步记忆示例
python async_memory_function_examples.py
```

## 注意事项

- 异步功能需要 Python 3.8+ 版本
- 请确保安全处理 API 密钥和敏感信息
- 在生产环境中，请将模拟的 API 调用替换为实际实现
- 遵循提示模板中的工具调用规则
- 为每个函数调用使用唯一的 call_id
- 为每个函数调用提供清晰的说明
- 异步流式处理时注意错误处理和资源释放
- 使用 `ResultManager` 管理多个函数调用的结果
- 在异步上下文中正确处理异常和超时
- 使用 `MemoryPromptManager` 管理对话上下文

## 系统要求

- Python 3.8 或更高版本

## 许可证

MIT 许可证 