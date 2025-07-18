# Discord-chatbot

基于Deepseek API的智能聊天机器人

## 功能特性
- 支持`!chat`指令交互
- 集成Deepseek大语言模型
- 自动重连机制

## 部署要求
- Python 3.8+
- Discord开发者账号
- Deepseek API密钥

## 快速启动
```bash
git clone https://github.com/您的账号/Discord-chatbot.git
pip install -r requirements.txt
```

## 环境变量说明
| 变量名             | 必填 | 说明                  |
|-------------------|------|---------------------|
| DISCORD_TOKEN     | 是   | Discord机器人令牌      |
| DEEPSEEK_API_KEY  | 是   | Deepseek API密钥      |
| ENV               | 否   | 环境标识(dev/prod)    |

## 部署指南
```bash
# 生产环境部署
docker build -t discord-bot .
docker run -d -e DISCORD_TOKEN=xxx -e DEEPSEEK_API_KEY=xxx discord-bot
```