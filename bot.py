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

# 添加对话历史记录字典
conversation_history = {}

async def call_deepseek_api(user_id: int, message_content: str) -> str:
    # 维护对话历史
    if user_id not in conversation_history:
        conversation_history[user_id] = []
    
    conversation_history[user_id].append({"role": "user", "content": message_content})
    
    # 控制历史长度（保留最近5轮对话）
    if len(conversation_history[user_id]) > 10:
        conversation_history[user_id] = conversation_history[user_id][-10:]
    
    headers = {
        "Authorization": f"Bearer {os.getenv('DEEPSEEK_API_KEY')}",
        "Content-Type": "application/json"
    }
    
    data = {
        "model": "deepseek-chat",
        "messages": conversation_history[user_id][-5:]  # 仅发送最近5条历史
    }

    try:
        response = requests.post(DEEPSEEK_API_URL, json=data, headers=headers)
        response.raise_for_status()
        response_content = response.json()['choices'][0]['message']['content']
        
        # 将AI回复加入历史
        conversation_history[user_id].append({"role": "assistant", "content": response_content})
        
        return response_content
    except Exception as e:
        return f"API请求失败: {str(e)}"

@client.event
async def on_ready():
    print(f'已登录为 {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    # 新增重置指令
    if message.content == '!reset':
        user_id = message.author.id
        if user_id in conversation_history:
            del conversation_history[user_id]
            await message.channel.send("✅ 您的对话上下文已重置")
        else:
            await message.channel.send("ℹ️ 没有需要重置的对话记录")
        return

    if message.content.startswith('!chat '):
        query = message.content[6:].strip()
        if not query:
            await message.channel.send("请输入有效问题")
            return

        async with message.channel.typing():
            # 使用用户ID作为对话标识
            user_id = message.author.id
            response = await call_deepseek_api(user_id, query)
            await message.channel.send(response[:2000])

if not os.getenv('DISCORD_TOKEN'):
    raise ValueError("DISCORD_TOKEN环境变量未配置")
client.run(os.getenv('DISCORD_TOKEN') or os.environ['DISCORD_TOKEN'], reconnect=True)  # 添加重连参数