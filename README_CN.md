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
from mfcs.function_calling import FunctionCallingPromptGenerator

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
template = FunctionCallingPromptGenerator.generate_function_prompt(functions)
```

### 2. 解析输出中的函数调用

```python
from mfcs.function_calling import StreamParser

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
parser = StreamParser()
content, tool_calls = parser.parse_output(output)
print(f"内容: {content}")
print(f"函数调用: {tool_calls}")
```

### 3. 处理流式输出

```python
from mfcs.function_calling import StreamParser

# 处理流式输出
parser = StreamParser()

# 在流式循环中
for chunk in stream:
    content, tool_calls = parser.parse_stream_output(chunk)
    if content:
        print(content, end="", flush=True)
    if tool_calls:
        for tool_call in tool_calls:
            print(f"函数 {tool_call['name']} 被调用，参数: {tool_call['arguments']}")
```

### 4. 异步流式处理与函数调用

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
                # 处理函数调用
                result = await process_function_call(tool_call)
                # 添加结果
                api_results.add_result(tool_call['call_id'], tool_call['name'], result)
    
    # 获取所有结果
    results = api_results.get_api_results()
```

## 示例

查看 `examples` 目录获取更详细的示例：

- `function_calling_examples.py`：基本函数调用示例
- `async_function_calling_examples.py`：异步流式处理示例

## 注意事项

- 异步功能需要 Python 3.7+ 版本
- 请确保安全处理 API 密钥和敏感信息
- 在生产环境中，请将模拟的 API 调用替换为实际实现
- 遵循提示模板中的工具调用规则
- 为每个函数调用使用唯一的 call_id
- 为每个函数调用提供清晰的说明

## 系统要求

- Python 3.8 或更高版本

## 许可证

MIT 许可证 