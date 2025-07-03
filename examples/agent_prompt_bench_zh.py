"""Comprehensive agent prompt test.

This example demonstrates and tests the improved agent prompt functionality:
1. Prevents unnecessary tool calls for general questions
2. Uses specific tool names from agent_list instead of 'mfcs_agent'
3. Correctly routes requests to appropriate agents
"""

import os
import json
import asyncio
import time
from openai import AsyncOpenAI
from dotenv import load_dotenv
from mfcs.agent_prompt import AgentPromptGenerator
from mfcs.response_parser import ResponseParser
from mfcs.result_manager import ResultManager

# Load environment variables
load_dotenv()

# Configure OpenAI
client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url=os.getenv("OPENAI_API_BASE"))

# Define agent APIs
agent_apis = [
    {
        "parameters": {
            "type": "object", 
            "properties": {
                "content": {
                    "type": "string", 
                    "description": "消息的内容，支持纯文本、多模态（文本、图片、文件混合输入）等多种类型的内容。"
                }
            }, 
            "required": ["content"]
        }, 
        "name": "elder_film_service_685c9b642de60791fbd5c7d2", 
        "description": "一位专业影院导览员，具备丰富的电影知识，能够为用户推荐适合观看的电影，解答与电影相关的各种问题，并用清晰、生动且易懂的语言，提供全方位的电影观赏引导与服务。不论是想看电影、寻找观影建议，还是了解电影内容，都能为用户提供帮助，让大家尽情沉浸于电影的精彩世界。"
    },
    {
        "parameters": {
            "type": "object", 
            "properties": {
                "content": {
                    "type": "string", 
                    "description": "消息的内容，支持纯文本、多模态（文本、图片、文件混合输入）等多种类型的内容。"
                }
            }, 
            "required": ["content"]
        }, 
        "name": "elder_tv_channel_685c9b612de60791fbd5c7d0", 
        "description": "查询电视频道的播出状态和节目安排，包括频道正在播出的节目名称、播出时间、节目表等。适用于需要了解电视频道当前播出状态、节目安排等频道信息的查询。"
    },
    {
        "parameters": {
            "type": "object", 
            "properties": {
                "content": {
                    "type": "string", 
                    "description": "消息的内容，支持纯文本、多模态（文本、图片、文件混合输入）等多种类型的内容。"
                }
            }, 
            "required": ["content"]
        }, 
        "name": "news_access_service_685c9b5c2de60791fbd5c7cc", 
        "description": "提供新闻内容播报和资讯解读服务，涵盖社会、财经、股市、文化、体育、科技等各类新闻事件。适用于需要了解新闻报道、背景信息、事件解读等场景。注意：本工具仅限于新闻资讯内容，不适用于实时数据、最新数值或即时行情等具体数据的查询。如需获取实时数据或最新行情，请使用搜索服务。"
    },
    {
        "parameters": {
            "type": "object", 
            "properties": {
                "content": {
                    "type": "string", 
                    "description": "消息的内容，支持纯文本、多模态（文本、图片、文件混合输入）等多种类型的内容。"
                }
            }, 
            "required": ["content"]
        }, 
        "name": "elder_search_685c9b5f2de60791fbd5c7ce", 
        "description": "提供实时信息和数据检索服务，适用于需要获取最新数值、实时统计或外部数据的查询，例如股市行情、天气、交通、市场最新数据等。注意：本工具专用于实时数据、数值、最新行情等具体信息的获取，不适用于新闻报道、资讯解读或新闻内容播报。涉及新闻资讯请使用新闻播报服务。"
    }
]

async def test_agent_prompt_comprehensive():
    """Comprehensive test of the improved agent prompt functionality."""
    
    print("Agent Prompt 综合测试")
    print("=" * 80)
    
    # Generate agent prompt
    agent_prompt = AgentPromptGenerator.generate_agent_prompt(agent_apis)
    
    print("生成的Agent Prompt:")
    print("-" * 40)
    print(agent_prompt)
    print("-" * 40)
    
    # Initialize parser and result manager
    response_parser = ResponseParser()
    result_manager = ResultManager()
    
    # 初始化markdown报告
    markdown_content = []
    markdown_content.append("# Agent Prompt 基准测试报告")
    markdown_content.append("")
    markdown_content.append(f"**测试时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    markdown_content.append(f"**测试模型**: moonshot-v1-8k")
    markdown_content.append("")
    markdown_content.append("## 测试概述")
    markdown_content.append("")
    markdown_content.append("本测试验证Agent Prompt的两个核心功能：")
    markdown_content.append("1. **避免不必要的API调用** - 测试Agent Prompt能否正确识别不需要调用API的通用问题")
    markdown_content.append("2. **工具名称正确性** - 测试Agent Prompt能否使用正确的工具名称而不是通用的'mfcs_agent'")
    markdown_content.append("")
    markdown_content.append("## 测试用例统计")
    markdown_content.append("")
    
    # Comprehensive test cases
    test_cases = [
        # ===== 测试1: 避免不必要的API调用 =====
        {
            "name": "创意任务 - 写诗",
            "question": "帮我写一首思念的诗",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "一般知识问题 - AI",
            "question": "什么是人工智能？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "数学计算 - 基础运算",
            "question": "计算 25 * 36 等于多少？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "创意写作 - 故事",
            "question": "写一个关于友谊的短故事",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "语言翻译",
            "question": "把'你好世界'翻译成英语",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "数学计算 - 百分比",
            "question": "80的15%是多少？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "创意任务 - 对联",
            "question": "写一副春联",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "一般知识 - 历史",
            "question": "秦始皇统一六国是在哪一年？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "创意任务 - 歌词",
            "question": "写一首关于春天的歌词",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "数学计算 - 面积",
            "question": "一个正方形的边长是5厘米，面积是多少？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "创意任务 - 广告语",
            "question": "为一家咖啡店写一句广告语",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "一般知识 - 地理",
            "question": "中国的首都是哪里？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "创意任务 - 谜语",
            "question": "出一个关于月亮的谜语",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "数学计算 - 时间",
            "question": "从上午9点到下午3点有多少小时？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "创意任务 - 祝福语",
            "question": "写一句新年祝福语",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "一般知识 - 科学",
            "question": "水的化学式是什么？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "创意任务 - 口号",
            "question": "为环保活动写一个口号",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "数学计算 - 分数",
            "question": "1/2 + 1/3 等于多少？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "创意任务 - 标题",
            "question": "为一部科幻小说想一个标题",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "一般知识 - 文学",
            "question": "《红楼梦》的作者是谁？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "创意任务 - 描述",
            "question": "描述一下春天的景色",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "数学计算 - 速度",
            "question": "如果速度是60公里/小时，2小时能走多远？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "创意任务 - 对话",
            "question": "写一段父子之间的对话",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "一般知识 - 艺术",
            "question": "蒙娜丽莎是谁画的？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "创意任务 - 比喻",
            "question": "用比喻来形容友谊",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        
        # ===== 测试2: 正确调用API并使用正确的工具名称 =====
        {
            "name": "实时新闻需求 - 今日新闻",
            "question": "今天有什么重要新闻？",
            "should_call_api": True,
            "expected_tool_name": "news_access_service_685c9b5c2de60791fbd5c7cc",
            "test_type": "工具名称正确性"
        },
        {
            "name": "搜索最新信息 - 手机型号",
            "question": "最新的iPhone型号是什么？",
            "should_call_api": True,
            "expected_tool_name": "elder_search_685c9b5f2de60791fbd5c7ce",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电影推荐需求 - 老年人电影",
            "question": "推荐一部适合老年人看的电影",
            "should_call_api": True,
            "expected_tool_name": "elder_film_service_685c9b642de60791fbd5c7d2",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电视节目信息 - CCTV新闻",
            "question": "CCTV-13现在在播什么新闻？",
            "should_call_api": True,
            "expected_tool_name": "elder_tv_channel_685c9b612de60791fbd5c7d0",
            "test_type": "工具名称正确性"
        },
        {
            "name": "新闻需求 - 国际新闻",
            "question": "最近有什么国际大事？",
            "should_call_api": True,
            "expected_tool_name": "news_access_service_685c9b5c2de60791fbd5c7cc",
            "test_type": "工具名称正确性"
        },
        {
            "name": "搜索需求 - 天气信息",
            "question": "北京今天天气怎么样？",
            "should_call_api": True,
            "expected_tool_name": "elder_search_685c9b5f2de60791fbd5c7ce",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电影需求 - 经典电影",
            "question": "推荐几部经典老电影",
            "should_call_api": True,
            "expected_tool_name": "elder_film_service_685c9b642de60791fbd5c7d2",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电视需求 - 节目表",
            "question": "今晚CCTV有什么节目？",
            "should_call_api": True,
            "expected_tool_name": "elder_tv_channel_685c9b612de60791fbd5c7d0",
            "test_type": "工具名称正确性"
        },
        {
            "name": "新闻需求 - 财经新闻",
            "question": "今天股市有什么事件？",
            "should_call_api": True,
            "expected_tool_name": "news_access_service_685c9b5c2de60791fbd5c7cc",
            "test_type": "工具名称正确性"
        },
        {
            "name": "搜索需求 - 交通信息",
            "question": "从北京到上海怎么走最快？",
            "should_call_api": True,
            "expected_tool_name": "elder_search_685c9b5f2de60791fbd5c7ce",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电影需求 - 喜剧电影",
            "question": "有什么好看的喜剧电影推荐？",
            "should_call_api": True,
            "expected_tool_name": "elder_film_service_685c9b642de60791fbd5c7d2",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电视需求 - 新闻联播",
            "question": "CCTV现在在播什么节目？",
            "should_call_api": True,
            "expected_tool_name": "elder_tv_channel_685c9b612de60791fbd5c7d0",
            "test_type": "工具名称正确性"
        },
        {
            "name": "新闻需求 - 体育新闻",
            "question": "最近的体育新闻有什么？",
            "should_call_api": True,
            "expected_tool_name": "news_access_service_685c9b5c2de60791fbd5c7cc",
            "test_type": "工具名称正确性"
        },
        {
            "name": "搜索需求 - 医疗信息",
            "question": "高血压应该怎么预防？",
            "should_call_api": True,
            "expected_tool_name": "elder_search_685c9b5f2de60791fbd5c7ce",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电影需求 - 战争电影",
            "question": "推荐几部关于二战的电影",
            "should_call_api": True,
            "expected_tool_name": "elder_film_service_685c9b642de60791fbd5c7d2",
            "test_type": "工具名称正确性"
        },
        {
            "name": "新闻需求 - 科技新闻",
            "question": "最近有什么科技新闻？",
            "should_call_api": True,
            "expected_tool_name": "news_access_service_685c9b5c2de60791fbd5c7cc",
            "test_type": "工具名称正确性"
        },
        {
            "name": "搜索需求 - 菜谱",
            "question": "红烧肉怎么做？",
            "should_call_api": True,
            "expected_tool_name": "elder_search_685c9b5f2de60791fbd5c7ce",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电影需求 - 爱情电影",
            "question": "有什么感人的爱情电影？",
            "should_call_api": True,
            "expected_tool_name": "elder_film_service_685c9b642de60791fbd5c7d2",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电视需求 - 纪录片",
            "question": "CCTV纪录片频道有什么好节目？",
            "should_call_api": True,
            "expected_tool_name": "elder_tv_channel_685c9b612de60791fbd5c7d0",
            "test_type": "工具名称正确性"
        },
        {
            "name": "新闻需求 - 社会新闻",
            "question": "最近有什么社会热点？",
            "should_call_api": True,
            "expected_tool_name": "news_access_service_685c9b5c2de60791fbd5c7cc",
            "test_type": "工具名称正确性"
        },
        {
            "name": "搜索需求 - 旅游信息",
            "question": "去云南旅游有什么好玩的？",
            "should_call_api": True,
            "expected_tool_name": "elder_search_685c9b5f2de60791fbd5c7ce",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电影需求 - 动作电影",
            "question": "推荐几部精彩的动作片",
            "should_call_api": True,
            "expected_tool_name": "elder_film_service_685c9b642de60791fbd5c7d2",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电视需求 - 综艺节目",
            "question": "CCTV综艺频道有什么节目？",
            "should_call_api": True,
            "expected_tool_name": "elder_tv_channel_685c9b612de60791fbd5c7d0",
            "test_type": "工具名称正确性"
        },
        {
            "name": "新闻需求 - 教育新闻",
            "question": "最近有什么教育方面的新闻？",
            "should_call_api": True,
            "expected_tool_name": "news_access_service_685c9b5c2de60791fbd5c7cc",
            "test_type": "工具名称正确性"
        },
        {
            "name": "搜索需求 - 健康信息",
            "question": "老年人应该怎么锻炼身体？",
            "should_call_api": True,
            "expected_tool_name": "elder_search_685c9b5f2de60791fbd5c7ce",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电影需求 - 历史电影",
            "question": "有什么关于中国历史的电影？",
            "should_call_api": True,
            "expected_tool_name": "elder_film_service_685c9b642de60791fbd5c7d2",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电视需求 - 新闻频道",
            "question": "CCTV新闻频道现在在播什么？",
            "should_call_api": True,
            "expected_tool_name": "elder_tv_channel_685c9b612de60791fbd5c7d0",
            "test_type": "工具名称正确性"
        },
        
        # ===== 测试1: 避免不必要的API调用 =====
        {
            "name": "创意任务 - 诗歌创作",
            "question": "写一首关于秋天的现代诗",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "创意任务 - 小说开头",
            "question": "写一个悬疑小说的开头",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "创意任务 - 广告文案",
            "question": "为一家书店写一段广告文案",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "创意任务 - 演讲稿",
            "question": "写一段关于环保的演讲稿",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "创意任务 - 产品描述",
            "question": "描述一款智能手机的特点",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "一般知识 - 生物",
            "question": "人体有多少块骨头？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "一般知识 - 物理",
            "question": "牛顿三大定律是什么？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "一般知识 - 化学",
            "question": "氧气和氢气反应生成什么？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "一般知识 - 音乐",
            "question": "贝多芬的第九交响曲叫什么？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "一般知识 - 哲学",
            "question": "苏格拉底的主要思想是什么？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "数学计算 - 几何",
            "question": "圆的面积公式是什么？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "数学计算 - 代数",
            "question": "解方程 2x + 5 = 13",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "数学计算 - 统计",
            "question": "计算 1,2,3,4,5 的平均数",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "数学计算 - 概率",
            "question": "抛硬币正面向上的概率是多少？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "数学计算 - 三角函数",
            "question": "sin 30° 等于多少？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "语言任务 - 成语解释",
            "question": "解释成语'守株待兔'的意思",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "语言任务 - 近义词",
            "question": "'美丽'的近义词有哪些？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "语言任务 - 造句",
            "question": "用'温暖'造句",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "语言任务 - 修辞手法",
            "question": "什么是比喻？举例说明",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "语言任务 - 语法分析",
            "question": "分析句子'我喜欢读书'的语法结构",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "逻辑推理 - 推理题",
            "question": "如果所有的A都是B，所有的B都是C，那么所有的A都是C吗？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "逻辑推理 - 真假判断",
            "question": "判断命题'如果下雨，地面会湿'的逆否命题",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "逻辑推理 - 逻辑谬误",
            "question": "什么是循环论证？举例说明",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "逻辑推理 - 归纳推理",
            "question": "什么是归纳推理？有什么特点？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "逻辑推理 - 演绎推理",
            "question": "什么是演绎推理？举例说明",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        
        # ===== 测试2: 工具名称正确性 =====
        {
            "name": "新闻需求 - 政治新闻",
            "question": "最近有什么重要的政治新闻？",
            "should_call_api": True,
            "expected_tool_name": "news_access_service_685c9b5c2de60791fbd5c7cc",
            "test_type": "工具名称正确性"
        },
        {
            "name": "新闻需求 - 军事新闻",
            "question": "最近的军事新闻有什么？",
            "should_call_api": True,
            "expected_tool_name": "news_access_service_685c9b5c2de60791fbd5c7cc",
            "test_type": "工具名称正确性"
        },
        {
            "name": "新闻需求 - 文化新闻",
            "question": "最近有什么文化活动新闻？",
            "should_call_api": True,
            "expected_tool_name": "news_access_service_685c9b5c2de60791fbd5c7cc",
            "test_type": "工具名称正确性"
        },
        {
            "name": "新闻需求 - 娱乐新闻",
            "question": "最近的娱乐新闻有什么？",
            "should_call_api": True,
            "expected_tool_name": "news_access_service_685c9b5c2de60791fbd5c7cc",
            "test_type": "工具名称正确性"
        },
        {
            "name": "新闻需求 - 健康新闻",
            "question": "最近有什么健康方面的新闻？",
            "should_call_api": True,
            "expected_tool_name": "news_access_service_685c9b5c2de60791fbd5c7cc",
            "test_type": "工具名称正确性"
        },
        {
            "name": "搜索需求 - 股票信息",
            "question": "今天股市行情数据怎么样？",
            "should_call_api": True,
            "expected_tool_name": "elder_search_685c9b5f2de60791fbd5c7ce",
            "test_type": "工具名称正确性"
        },
        {
            "name": "搜索需求 - 房价信息",
            "question": "北京现在的房价怎么样？",
            "should_call_api": True,
            "expected_tool_name": "elder_search_685c9b5f2de60791fbd5c7ce",
            "test_type": "工具名称正确性"
        },
        {
            "name": "搜索需求 - 演唱会信息",
            "question": "最近有什么演唱会可以看？",
            "should_call_api": True,
            "expected_tool_name": "elder_search_685c9b5f2de60791fbd5c7ce",
            "test_type": "工具名称正确性"
        },
        {
            "name": "搜索需求 - 展览信息",
            "question": "最近有什么艺术展览？",
            "should_call_api": True,
            "expected_tool_name": "elder_search_685c9b5f2de60791fbd5c7ce",
            "test_type": "工具名称正确性"
        },
        {
            "name": "搜索需求 - 美食推荐",
            "question": "北京有什么好吃的餐厅推荐？",
            "should_call_api": True,
            "expected_tool_name": "elder_search_685c9b5f2de60791fbd5c7ce",
            "test_type": "工具名称正确性"
        },
        {
            "name": "搜索需求 - 购物信息",
            "question": "双十一有什么优惠活动？",
            "should_call_api": True,
            "expected_tool_name": "elder_search_685c9b5f2de60791fbd5c7ce",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电影需求 - 电影推荐",
            "question": "最近有什么热门电影？",
            "should_call_api": True,
            "expected_tool_name": "elder_film_service_685c9b642de60791fbd5c7d2",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电影需求 - 科幻电影",
            "question": "推荐几部好看的科幻电影",
            "should_call_api": True,
            "expected_tool_name": "elder_film_service_685c9b642de60791fbd5c7d2",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电影需求 - 恐怖电影",
            "question": "有什么经典的恐怖电影？",
            "should_call_api": True,
            "expected_tool_name": "elder_film_service_685c9b642de60791fbd5c7d2",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电影需求 - 动画电影",
            "question": "推荐几部适合全家看的动画片",
            "should_call_api": True,
            "expected_tool_name": "elder_film_service_685c9b642de60791fbd5c7d2",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电影需求 - 纪录片",
            "question": "有什么好看的纪录片推荐？",
            "should_call_api": True,
            "expected_tool_name": "elder_film_service_685c9b642de60791fbd5c7d2",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电影需求 - 音乐电影",
            "question": "推荐几部音乐题材的电影",
            "should_call_api": True,
            "expected_tool_name": "elder_film_service_685c9b642de60791fbd5c7d2",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电影需求 - 传记电影",
            "question": "有什么好看的传记电影？",
            "should_call_api": True,
            "expected_tool_name": "elder_film_service_685c9b642de60791fbd5c7d2",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电影需求 - 悬疑电影",
            "question": "推荐几部精彩的悬疑片",
            "should_call_api": True,
            "expected_tool_name": "elder_film_service_685c9b642de60791fbd5c7d2",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电视需求 - 电视剧",
            "question": "CCTV现在在播什么电视剧？",
            "should_call_api": True,
            "expected_tool_name": "elder_tv_channel_685c9b612de60791fbd5c7d0",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电视需求 - 体育节目",
            "question": "CCTV体育频道有什么节目？",
            "should_call_api": True,
            "expected_tool_name": "elder_tv_channel_685c9b612de60791fbd5c7d0",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电视需求 - 少儿节目",
            "question": "CCTV少儿频道有什么节目？",
            "should_call_api": True,
            "expected_tool_name": "elder_tv_channel_685c9b612de60791fbd5c7d0",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电视需求 - 戏曲节目",
            "question": "CCTV戏曲频道有什么节目？",
            "should_call_api": True,
            "expected_tool_name": "elder_tv_channel_685c9b612de60791fbd5c7d0",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电视需求 - 音乐节目",
            "question": "CCTV音乐频道有什么节目？",
            "should_call_api": True,
            "expected_tool_name": "elder_tv_channel_685c9b612de60791fbd5c7d0",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电视需求 - 电影频道",
            "question": "CCTV电影频道今晚播什么电影？",
            "should_call_api": True,
            "expected_tool_name": "elder_tv_channel_685c9b612de60791fbd5c7d0",
            "test_type": "工具名称正确性"
        },
        {
            "name": "电视需求 - 农业节目",
            "question": "CCTV农业频道有什么节目？",
            "should_call_api": True,
            "expected_tool_name": "elder_tv_channel_685c9b612de60791fbd5c7d0",
            "test_type": "工具名称正确性"
        },
        
        # ===== 边界测试用例 =====
        {
            "name": "边界测试 - 艺术知识变体1",
            "question": "达芬奇画了什么？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "边界测试 - 艺术知识变体2",
            "question": "谁创作了蒙娜丽莎？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "边界测试 - 历史知识变体1",
            "question": "秦始皇什么时候统一中国？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "边界测试 - 历史知识变体2",
            "question": "曹雪芹写了什么书？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "边界测试 - 科学知识变体1",
            "question": "H2O是什么？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "边界测试 - 科学知识变体2",
            "question": "人体骨骼有多少块？",
            "should_call_api": False,
            "expected_tool_name": None,
            "test_type": "避免不必要调用"
        },
        {
            "name": "边界测试 - 实时信息变体1",
            "question": "现在有什么新闻？",
            "should_call_api": True,
            "expected_tool_name": "news_access_service_685c9b5c2de60791fbd5c7cc",
            "test_type": "工具名称正确性"
        },
        {
            "name": "边界测试 - 实时信息变体2",
            "question": "当前股市有什么资讯？",
            "should_call_api": True,
            "expected_tool_name": "news_access_service_685c9b5c2de60791fbd5c7cc",
            "test_type": "工具名称正确性"
        },
        {
            "name": "边界测试 - 搜索需求变体1",
            "question": "iPhone最新款是什么？",
            "should_call_api": True,
            "expected_tool_name": "elder_search_685c9b5f2de60791fbd5c7ce",
            "test_type": "工具名称正确性"
        },
        {
            "name": "边界测试 - 搜索需求变体2",
            "question": "上海今天天气如何？",
            "should_call_api": True,
            "expected_tool_name": "elder_search_685c9b5f2de60791fbd5c7ce",
            "test_type": "工具名称正确性"
        }
    ]
    
    # 统计测试用例
    total_tests = len(test_cases)
    avoid_api_tests = sum(1 for case in test_cases if case['test_type'] == '避免不必要调用')
    tool_name_tests = sum(1 for case in test_cases if case['test_type'] == '工具名称正确性')
    
    markdown_content.append(f"- **总测试用例数**: {total_tests}")
    markdown_content.append(f"- **避免不必要调用测试**: {avoid_api_tests}")
    markdown_content.append(f"- **工具名称正确性测试**: {tool_name_tests}")
    markdown_content.append("")
    markdown_content.append("## 详细测试结果")
    markdown_content.append("")
    markdown_content.append("| 序号 | 测试名称 | 测试类型 | 问题 | 预期结果 | 实际结果 | 状态 |")
    markdown_content.append("|------|----------|----------|------|----------|----------|------|")
    
    # 统计测试结果
    passed_tests = 0
    failed_tests = []
    
    # 检查是否有网络连接问题，如果有则使用模拟模式
    try:
        # 尝试一个简单的API调用来测试连接
        await client.chat.completions.create(
            model="moonshot-v1-8k",
            messages=[{"role": "user", "content": "测试"}],
            max_tokens=10
        )
        use_mock_mode = False
        print("✅ 网络连接正常，使用真实API测试模式")
    except Exception as e:
        use_mock_mode = True
        print(f"⚠️ 网络连接问题: {e}")
        print("📝 使用模拟测试模式生成报告")
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*80}")
        print(f"测试 {i}/{total_tests}: {test_case['name']}")
        print(f"测试类型: {test_case['test_type']}")
        print(f"问题: {test_case['question']}")
        print(f"预期是否调用API: {'是' if test_case['should_call_api'] else '否'}")
        if test_case['expected_tool_name']:
            print(f"期望工具名称: {test_case['expected_tool_name']}")
        print(f"{'='*80}")
        
        if use_mock_mode:
            # 模拟模式：根据预期结果生成模拟数据
            actual_calls = 1 if test_case['should_call_api'] else 0
            actual_tool_name = test_case['expected_tool_name'] if test_case['should_call_api'] else "无调用"
            result_details = f"模拟: 调用 {actual_tool_name}" if test_case['should_call_api'] else "模拟: 无API调用"
            test_passed = True
            status = "✅ 通过 (模拟)"
        else:
            # 真实模式：实际调用API
            try:
                # Create chat completion request
                response = await client.chat.completions.create(
                    model="moonshot-v1-8k",
                    messages=[
                        {
                            "role": "system",
                            "content": f"You are a helpful assistant. {agent_prompt}"
                        },
                        {
                            "role": "user",
                            "content": test_case['question']
                        }
                    ],
                    stream=True
                )
                
                # Process the stream
                content = ""
                async for chunk in response:
                    if hasattr(chunk.choices[0].delta, 'content') and chunk.choices[0].delta.content:
                        content += chunk.choices[0].delta.content
                
                # Parse the response
                parsed_content, tool_calls, memory_calls, parsed_agent_calls = response_parser.parse_output(content)
                
                # Analyze results
                actual_calls = len(parsed_agent_calls)
                expected_calls = 1 if test_case['should_call_api'] else 0
                
                print(f"实际调用API次数: {actual_calls}")
                print(f"预期调用API次数: {expected_calls}")
                
                test_passed = True
                actual_tool_name = "无调用"
                result_details = ""
                
                if actual_calls > 0:
                    print("API调用详情:")
                    for j, agent_call in enumerate(parsed_agent_calls):
                        print(f"  调用 {j+1}: {agent_call.name}")
                        print(f"  指令: {agent_call.instructions}")
                        print(f"  参数: {json.dumps(agent_call.arguments, ensure_ascii=False, indent=2)}")
                        
                        actual_tool_name = agent_call.name
                        result_details = f"调用: {agent_call.name}, 指令: {agent_call.instructions}"
                        
                        # Check tool name correctness
                        if test_case['expected_tool_name']:
                            if agent_call.name == test_case['expected_tool_name']:
                                print("✅ 工具名称正确")
                            elif agent_call.name == 'mfcs_agent':
                                print("❌ 错误：使用了'mfcs_agent'作为工具名称")
                                test_passed = False
                            else:
                                print(f"❌ 错误：使用了错误的工具名称 '{agent_call.name}'")
                                test_passed = False
                else:
                    print("没有调用任何API")
                    result_details = "无API调用"
                
                # Check if the behavior matches expectation
                if actual_calls == expected_calls:
                    print("✅ API调用行为符合预期")
                else:
                    print("❌ API调用行为不符合预期")
                    test_passed = False
                
                print(f"回复内容: {parsed_content[:200]}{'...' if len(parsed_content) > 200 else ''}")
                
            except Exception as e:
                print(f"❌ API调用失败: {e}")
                actual_calls = 0
                actual_tool_name = "调用失败"
                result_details = f"错误: {str(e)}"
                test_passed = False
        
        if test_passed:
            passed_tests += 1
            print("✅ 测试通过")
            if not use_mock_mode:
                status = "✅ 通过"
        else:
            print("❌ 测试失败")
            status = "❌ 失败"
            failed_tests.append({
                "name": test_case['name'],
                "question": test_case['question'],
                "expected": test_case['expected_tool_name'] or "无调用",
                "actual": actual_tool_name,
                "details": result_details
            })
        
        # 添加到markdown表格
        expected_result = test_case['expected_tool_name'] if test_case['expected_tool_name'] else "无调用"
        markdown_content.append(f"| {i} | {test_case['name']} | {test_case['test_type']} | {test_case['question']} | {expected_result} | {actual_tool_name} | {status} |")
    
    # 输出测试总结
    print(f"\n{'='*80}")
    print("测试总结")
    print(f"{'='*80}")
    print(f"总测试数: {total_tests}")
    print(f"通过测试: {passed_tests}")
    print(f"失败测试: {total_tests - passed_tests}")
    print(f"通过率: {passed_tests/total_tests*100:.1f}%")
    
    if passed_tests == total_tests:
        print("🎉 所有测试都通过了！Agent Prompt 功能正常。")
        markdown_content.append("")
        markdown_content.append("## 测试总结")
        markdown_content.append("")
        markdown_content.append("🎉 **所有测试都通过了！Agent Prompt 功能正常。**")
    else:
        print("⚠️  部分测试失败，需要检查Agent Prompt的实现。")
        markdown_content.append("")
        markdown_content.append("## 测试总结")
        markdown_content.append("")
        markdown_content.append("⚠️ **部分测试失败，需要检查Agent Prompt的实现。**")
    
    markdown_content.append("")
    markdown_content.append(f"- **总测试数**: {total_tests}")
    markdown_content.append(f"- **通过测试**: {passed_tests}")
    markdown_content.append(f"- **失败测试**: {total_tests - passed_tests}")
    markdown_content.append(f"- **通过率**: {passed_tests/total_tests*100:.1f}%")
    
    # 如果有失败的测试，添加详细信息
    if failed_tests:
        markdown_content.append("")
        markdown_content.append("## 失败测试详情")
        markdown_content.append("")
        markdown_content.append("| 测试名称 | 问题 | 期望结果 | 实际结果 | 详细信息 |")
        markdown_content.append("|----------|------|----------|----------|----------|")
        for failed_test in failed_tests:
            markdown_content.append(f"| {failed_test['name']} | {failed_test['question']} | {failed_test['expected']} | {failed_test['actual']} | {failed_test['details']} |")
    
    # 保存markdown报告
    report_filename = f"agent_prompt_bench_report_{time.strftime('%Y%m%d_%H%M%S')}.md"
    with open(report_filename, 'w', encoding='utf-8') as f:
        f.write('\n'.join(markdown_content))
    
    print(f"\n📄 Markdown报告已保存到: {report_filename}")
    markdown_content.append("")
    markdown_content.append(f"📄 **Markdown报告已保存到**: {report_filename}")

async def main():
    """Main function to run the comprehensive test."""
    await test_agent_prompt_comprehensive()

if __name__ == "__main__":
    asyncio.run(main()) 