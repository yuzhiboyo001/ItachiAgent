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
```
安装依赖
bash
pip install -r requirements.txt
语音功能配置
下载 GPT-SoVITS 整合包

启动 api.py 服务：

bash
python api.py
服务默认运行在 http://127.0.0.1:9880

取消 yuzhiboyo.py 中 process_tts_and_playback 函数的注释

启动项目
bash
python yuzhiboyo.py
项目结构
text
ItachiAgent/
├── yuzhiboyo.py              # 主程序入口
├── db_handler.py             # SQLite 数据库操作
├── rag_retriever.py          # RAG 检索器
├── tokenization_small100.py  # 翻译模型分词器
├── chroma_db/                # 向量数据库目录
├── itachi_knowledge_base/    # 火影忍者知识库源文件
└── requirements.txt          # 依赖列表
对话示例
text
宇智波明: 木叶村今天天气怎么样？
[get_weather] 开始执行，城市: 木叶村
宇智波鼬: 木叶村今日晴空万里...是个适合散步的日子。
可用工具
工具名称	功能说明
get_weather	查询任意城市天气
search_knowledge	搜索火影忍者知识库
get_poem	获取诗词名言
scraping_search	智能网页搜索
