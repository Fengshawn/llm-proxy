from sanic import Sanic, json, Request
from sanic.response import text
from sanic.exceptions import SanicException
import httpx
import os

# 初始化 Sanic 应用
app = Sanic("DeepSeekService")

# 从环境变量获取 DeepSeek API 密钥（需提前配置）
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "your-api-key")
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"  # 假设的 API 地址

# 定义请求超时时间（秒）
TIMEOUT = 30

@app.post("/v1/chat/completions")
async def deepseek_chat(request: Request):
    """
    调用 DeepSeek 的对话接口
    请求体格式示例:
    {
        "messages": [
            {"role": "user", "content": "你好"}
        ],
        "model": "deepseek-chat"
    }
    """
    try:
        # 验证请求体
        if not request.json:
            raise SanicException("Invalid JSON body", status_code=400)

        # 提取参数
        data = request.json
        messages = data.get("messages", [])
        model = data.get("model", "deepseek-chat")

        # 构造 DeepSeek 请求头
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }

        # 构造请求体
        payload = {
            "messages": messages,
            "model": model,
            "temperature": 0.7,
            "max_tokens": 500
        }

        # 异步发送请求到 DeepSeek
        async with httpx.AsyncClient(timeout=TIMEOUT) as client:
            response = await client.post(
                DEEPSEEK_API_URL,
                headers=headers,
                json=payload
            )
            response.raise_for_status()  # 自动处理 4xx/5xx 错误
            return json(response.json())

    except httpx.HTTPStatusError as e:
        return json({
            "error": f"DeepSeek API error: {e.response.text}",
            "status_code": e.response.status_code
        }, status=e.response.status_code)
    
    except Exception as e:
        return json({
            "error": f"Internal server error: {str(e)}"
        }, status=500)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, access_log=True)
