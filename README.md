# ItachiAgent - 宇智波鼬智能对话助手

基于 LangGraph 构建的多工具 Agent，集成 RAG 知识库、天气查询、网页爬虫、诗词 API，并配备日文翻译与 GPT-SoVITS 语音合成。

## 技术栈

- LangGraph + LangChain - Agent 框架
- DeepSeek API - LLM 推理
- ChromaDB - RAG 向量数据库
- M2M100 - 日文翻译模型
- GPT-SoVITS - 语音合成
- SQLite - 对话历史存储

## 功能特性

- 角色扮演：宇智波鼬对话风格
- 工具调用：天气查询、RAG检索、诗词获取、网页爬虫
- 日文翻译：本地 M2M100 模型 + 云端 API 双备
- 语音输出：GPT-SoVITS 日文语音合成
- 对话记忆：自动保存历史记录

## 环境配置

所有配置在 `yuzhiboyo.py` 中直接修改：

```python
# DeepSeek API Key
os.environ["DEEPSEEK_API_KEY"] = "your_deepseek_api_key"

# 模型缓存路径（可选）
os.environ["HF_HOME"] = "D:/huggingface_cache"
os.environ["TRANSFORMERS_CACHE"] = "D:/huggingface_cache/transformers"

# Uapi工具服务 Token
client = UapiClient("https://uapis.cn", token="your_uapi_token")
