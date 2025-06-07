import os
import discord
import requests
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

intents = discord.Intents.default()
intents.message_content = True  # 必须启用消息内容意图

# 生产环境移除代理配置（通过环境变量判断）
client = discord.Client(
    intents=intents,
    proxy=os.getenv('PROXY') if os.getenv('ENV') == 'dev' else None
)

async def call_deepseek_api(message_content: str) -> str:
    headers = {
        "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "user", "content": message_content}
        ]
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, json=data, headers=headers)
        response.raise_for_status()
        return response.json()['choices'][0]['message']['content']
    except Exception as e:
        return f"API请求失败: {str(e)}"

@client.event
async def on_ready():
    print(f'已登录为 {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('!chat '):
        query = message.content[6:].strip()
        if not query:
            await message.channel.send("请输入有效问题")
            return

        async with message.channel.typing():
            response = await call_deepseek_api(query)
            await message.channel.send(response[:2000])

if not os.getenv('DISCORD_TOKEN'):
    raise ValueError("DISCORD_TOKEN环境变量未配置")
client.run(os.getenv('DISCORD_TOKEN') or os.environ['DISCORD_TOKEN'], reconnect=True)  # 添加重连参数