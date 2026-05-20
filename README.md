# ItachiAgent - 宇智波鼬智能对话助手

基于 LangGraph 构建的多工具 Agent，集成 RAG 知识库、天气查询、网页爬虫、诗词 API，并配备日文翻译与 GPT-SoVITS 语音合成。

## 一键整合包配置

百度网盘链接：https://pan.baidu.com/s/1GDmLuMpLV8VpLNShYhhZNw?pwd=gzwz

下载完先修改yuzhiboyo.py的api_key，路径等配置，语音功能请看下文介绍，然后启动start_agent.bat，即可正常使用Agent服务。

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
## 语音功能配置

### 1. 下载 GPT-SoVITS 整合包

下载地址：https://github.com/RVC-Boss/GPT-SoVITS

### 2. 准备模型文件(整合包含有)

- SoVITS 权重：`SoVITS_weights_v2ProPlus/宇智波鼬plus_e8_s232.pth`
- GPT 权重：`GPT_weights_v2ProPlus/宇智波鼬plus-e15.ckpt`
- 参考音频：`you.wav` (日文参考语音)

### 3. 创建启动脚本 (start_tts_example.bat)

代码示例如下：

```batch
@echo off
set "SCRIPT_DIR=%~dp0"
set "SCRIPT_DIR=%SCRIPT_DIR:~0,-1%"
cd /d "%SCRIPT_DIR%"
set "PATH=%SCRIPT_DIR%\runtime;%PATH%"

runtime\python.exe api.py -hp ^
  -s "宇智波鼬plus_e8_s232.pth路径" ^
  -g "宇智波鼬plus-e15.ckpt路径" ^
  -dr "you.wav路径" ^
  -dt "他の忍びがここに駆けつけるだろう、目的を見失うな。" ^
  -dl "ja" ^
  -d "cuda" ^
  -a "127.0.0.1" ^
  -p 9880

pause
```
### 4. 启动TTS服务

双击运行 start_tts.bat

服务默认运行在 http://127.0.0.1:9880

### 5. 启用代码中的语音功能
取消 yuzhiboyo.py 中 process_tts_and_playback 函数的注释：

python
```
def process_tts_and_playback(chinese_text: str):
    ...
    # 2. TTS 生成
    audio_file = text_to_speech(japanese_text)      # 取消注释
    # 3. 播放
    if audio_file:                                   # 取消注释
        winsound.PlaySound(...)                      # 取消注释
```

## 技术栈

- LangGraph + LangChain - Agent 框架
- DeepSeek API - LLM 推理
- ChromaDB - RAG 向量数据库
- M2M100 - 日文翻译模型
- GPT-SoVITS - 语音合成
- SQLite - 对话历史存储
- Scrapling StealthyFetcher - 智能网页爬虫

## 核心功能

### 1. 角色扮演对话

- 模拟宇智波鼬冷静、内敛的说话风格
- 使用省略号和比喻性表达
- 保持角色背景一致性（身患重病、宇智波一族、佐助的哥哥）

### 2. RAG 知识库检索

- 基于 ChromaDB 向量数据库
- 知识库包含鼬的世界观、人物关系、能力设定、经典台词等 29 个文档
- 支持语义检索，返回最相关的 3 条知识

### 3. 多工具调用

| 工具名称 | 功能说明 |
|---------|---------|
| get_weather | 查询任意城市实时天气 |
| search_knowledge | 搜索火影忍者知识库 |
| get_poem | 获取随机诗词名言 |
| scraping_search | 智能网页爬虫搜索 |

### 4. 日文语音输出

- 中文回复自动翻译为日文（M2M100 本地模型 / Uapi 云端 API）
- 调用 GPT-SoVITS 生成鼬的日文语音
- 异步播放，不阻塞对话流程

### 5. 对话历史管理

- SQLite 本地存储
- 支持多会话（按 session_id 区分）
- 自动加载历史对话上下文

