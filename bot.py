import os
import discord
import requests
from dotenv import load_dotenv

load_dotenv()

DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"

intents = discord.Intents.default()
intents.message_content = True  # 必须启用消息内容意图（接收消息内容权限）

# 初始化Discord客户端（根据环境变量配置代理）
client = discord.Client(
    intents=intents,
    proxy=os.getenv('PROXY') if os.getenv('ENV') == 'dev' else None
)

# 用户对话上下文存储器（结构：{user_id: [message_obj...]})
conversation_history = {}

async def call_deepseek_api(user_id: int, message_content: str) -> str:
    """调用Deepseek API进行对话处理
    Args:
        user_id: 用户唯一标识（Discord用户ID）
        message_content: 用户输入的对话内容
    Returns:
        str: API响应内容或错误信息
    """
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
    """消息事件处理器"""
    # 防止机器人响应自身消息
    if message.author == client.user:
        return

    # 重置上下文指令处理
    if client.user.mentioned_in(message) and '/reset' in message.content:
        user_id = message.author.id
        try:
            if user_id in conversation_history:
                del conversation_history[user_id]
                await message.add_reaction('✅')
                await message.add_reaction('🔄')
            else:
                await message.add_reaction('ℹ️')
        except Exception as e:
            await message.add_reaction('❌')
            print(f"重置失败: {e}")
        return

    # 对话指令处理（指令格式：!chat <问题>）
    if message.content.startswith('!chat ') or client.user.mentioned_in(message):
        query = message.content.replace(f'<@{client.user.id}>', '').strip()
        if not query:
            await message.channel.send("请输入有效问题")
            return

        async with message.channel.typing():  # 显示"正在输入"状态
            # 使用用户ID作为对话标识
            user_id = message.author.id
            response = await call_deepseek_api(user_id, query)
            await message.channel.send(response[:2000])

# 启动前环境变量校验
if not os.getenv('DISCORD_TOKEN'):
    raise ValueError("DISCORD_TOKEN环境变量未配置")
    
# 启动机器人（启用自动重连机制）
client.run(os.getenv('DISCORD_TOKEN') or os.environ['DISCORD_TOKEN'], reconnect=True)