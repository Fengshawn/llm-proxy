from sanic import Sanic, json, Request
from sanic.response import text, HTTPResponse
from sanic.exceptions import SanicException
from openai import AsyncOpenAI
import asyncio
import os

# 初始化 Sanic 应用
app = Sanic("DeepSeekAsyncService")

# 配置 DeepSeek 客户端
client = AsyncOpenAI(
    api_key=os.getenv("DEEPSEEK_API_KEY", "your-api-key"),
    base_url="https://api.deepseek.com"
)


@app.get("/health")
async def health(request: Request):
    return json({
               "error": 
                   {
                       "message": "Service is ok~",
                        "type": "health_check",
                        "code": 200
                   }
               })

@app.post("/llm/chat/completions")
async def chat_completions(request: Request):
    """
    异步调用 DeepSeek 的对话接口
    请求体格式与官方一致：
    {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": "You are a helpful assistant"},
            {"role": "user", "content": "Hello"}
        ],
        "stream": false
    }
    """
    try:
        # 验证请求体
        if not request.json:
            raise SanicException("Invalid JSON body", status_code=400)

        # 提取参数（保持与官方 SDK 相同的参数结构）
        params = request.json
        required_params = ["model", "messages"]
        if any(param not in params for param in required_params):
            raise SanicException("Missing required parameters", status_code=400)
        
        stream_enabled = params.get("stream", False)
        if stream_enabled is False:
        # 异步调用 DeepSeek API
            response = await client.chat.completions.create(
                model=params["model"],
                messages=params["messages"],
                stream=stream_enabled, # False
                temperature=params.get("temperature", 0.7),
                max_tokens=params.get("max_tokens", 512)
            )

            # 构建与官方一致的响应格式
            return json({
                "id": response.id,
                "object": response.object,
                "created": response.created,
                "choices": [{
                    "index": choice.index,
                    "message": {
                        "role": choice.message.role,
                        "content": choice.message.content
                    },
                    "finish_reason": choice.finish_reason
                } for choice in response.choices],
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                }
            })
        else:
            response = await request.respond(content_type="text/plain")
            stream_response = await client.chat.completions.create(
                model=params["model"],
                messages=params["messages"],
                stream=stream_enabled, # True
                temperature=params.get("temperature", 0.7),
                max_tokens=params.get("max_tokens", 512)
            )
            async for chunk in stream_response:
            # 解析 JSON 数据
                if chunk.choices:  # 确保 choices 字段存在
                    content = chunk.choices[0].delta.content
                    print(type(content))
                    if content:
                        await response.send(content)  # 逐块写入响应
            await response.send("Stream completed.")
            await response.eof()
            return response

    except Exception as e:
        # 错误处理保持与官方响应格式一致
        error_msg = str(e)
        status_code = 500
        if hasattr(e, 'status_code'):
            status_code = e.status_code
        return json({
            "error": {
                "message": error_msg,
                "type": "api_error",
                "code": status_code
            }
        }, status=status_code)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, access_log=True, auto_reload=True)
