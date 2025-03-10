from sanic import Sanic, json, Request
from sanic.response import text
from sanic.exceptions import SanicException
from openai import AsyncOpenAI
from openai import OpenAI
import asyncio
import os

# 配置 DeepSeek 客户端
client = OpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY", "your-api-key"),
    base_url="https://api.deepseek.com"
)

response = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "user", "content": "Give me a 200-word introduction"},
    ],
    stream=True
)
for chunk in response: # 可以在该行设置断点，用户观察流式输出
    print(chunk.choices[0].delta.content, end="")  # 逐块输出回复
