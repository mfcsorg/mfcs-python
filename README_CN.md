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
- API 结果管理
- 多函数调用处理

## 安装

```bash
pip install -e .
```

## 使用方法

### 1. 生成函数调用提示模板

```python
from mfcs.function_calling.function_prompt import FunctionPromptGenerator

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
from mfcs.function_calling.response_parser import ResponseParser

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
                # 处理函数调用并存储结果
                result = await process_function_call(tool_call)
                api_results.add_api_result(tool_call['call_id'], tool_call['name'], result)
    
    # 获取所有处理结果
    return api_results.get_api_results()
```

## 示例

查看 `examples` 目录获取更详细的示例：

- `function_calling_examples.py`：基本函数调用示例
  - 函数提示生成
  - 函数调用解析
  - API 结果管理

- `async_function_calling_examples.py`：异步流式处理示例
  - 异步流式处理最佳实践
  - 并发函数调用处理
  - 异步错误处理和超时控制

- `mcp_client_example.py`：MCP 客户端集成示例
  - 基本 MCP 客户端设置
  - 函数注册
  - 工具调用实现

- `async_mcp_client_example.py`：异步 MCP 客户端示例
  - 异步 MCP 客户端配置
  - 异步工具调用实现
  - 并发任务处理

运行示例以查看库的实际效果：

```bash
# 运行基本示例
python examples/function_calling_examples.py
python examples/mcp_client_example.py

# 运行异步示例
python examples/async_function_calling_examples.py
python examples/async_mcp_client_example.py
```

## 注意事项

- 异步功能需要 Python 3.8+ 版本
- 请确保安全处理 API 密钥和敏感信息
- 在生产环境中，请将模拟的 API 调用替换为实际实现
- 遵循提示模板中的工具调用规则
- 为每个函数调用使用唯一的 call_id
- 为每个函数调用提供清晰的说明
- 异步流式处理时注意错误处理和资源释放
- 使用 `ApiResultManager` 管理多个函数调用的结果
- 在异步上下文中正确处理异常和超时

## 系统要求

- Python 3.8 或更高版本

## 许可证

MIT 许可证 