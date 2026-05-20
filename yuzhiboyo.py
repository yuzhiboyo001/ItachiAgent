import os
import re
import threading
import winsound
import requests
import time
# 设置加速器
# os.environ['HTTP_PROXY'] = 'socks5://127.0.0.1:7890'
# os.environ['HTTPS_PROXY'] = 'socks5://127.0.0.1:7890'
# os.environ["HF_TOKEN"] = "Hugingface的token"
# 关键：强制离线模式
os.environ["TRANSFORMERS_OFFLINE"] = "1"
os.environ["HF_HUB_OFFLINE"] = "1"
# 设置镜像
# os.environ["HF_ENDPOINT"] = "https://hf-mirror.com"
# 模型缓存路径
os.environ["HF_HOME"] = "D:/huggingface_cache"
os.environ["TRANSFORMERS_CACHE"] = "D:/huggingface_cache/transformers"
# 设置API_key
os.environ["DEEPSEEK_API_KEY"] = "API_key"


from langchain_deepseek import ChatDeepSeek
from langchain_core.prompts import ChatPromptTemplate
from langchain_classic.chains import create_retrieval_chain
from langchain_core.messages import AIMessage,HumanMessage
from rag_retriever import rag_retriever
from db_handler import init_db,load_conversation_history,save_conversation_round
from uapi import UapiClient
from uapi.errors import UapiError
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode, tools_condition
from transformers import M2M100ForConditionalGeneration
from tokenization_small100 import SMALL100Tokenizer
from scrapling import StealthyFetcher
from langgraph.graph import StateGraph, MessagesState, START, END

model = M2M100ForConditionalGeneration.from_pretrained("alirezamsh/small100", local_files_only=True)
tokenizer = SMALL100Tokenizer.from_pretrained("alirezamsh/small100", local_files_only=True)
retriever = rag_retriever()
init_db()
client = UapiClient("https://uapis.cn",token="工具服务API_token")

# 普通函数区
# 纯净翻译句子
def remove_parentheses_content(text: str) -> str:
    """
    删除中英文括号内的内容（包括括号本身）
    支持：（中文括号）、(英文括号)、（嵌套括号）
    """
    # 删除中文括号 （...） 内的内容
    text = re.sub(r'（[^（）]*）', '', text)
    # 删除英文括号 (...) 内的内容
    text = re.sub(r'\([^()]*\)', '', text)
    return text



# 中译日模块（云端API调用）
def translate_to_japanese_api(chinese_text:str)->str:
    try:
        result = client.translate.post_ai_translate(target_lang="ja", text=f"{chinese_text}")
        return result["data"]["translated_text"]
    except UapiError as exc:
        return f"API error: {exc}"
# 中译日模块（本地部署模型）
def translate_to_japanese_local(chinese_text:str)->str:
    """本地部署翻译，无延迟"""
    tokenizer.tgt_lang = "ja"
    encoded_zh = tokenizer(chinese_text, return_tensors="pt")
    generated_tokens = model.generate(
        **encoded_zh,
        max_length=512,
        num_beams=4,
        early_stopping=True,
        repetition_penalty=2.0,
    )
    return tokenizer.batch_decode(generated_tokens, skip_special_tokens=True)[0]
# AI语音模块
def text_to_speech(japanese_text:str)-> str | None:
    """
      调用 TTS API 生成语音，返回音频文件路径
      参数: japanese_text - 日文文本
      返回: 音频文件路径，失败返回 None
      """
    if not japanese_text:
        print("翻译文本为空")
        return ""
    try:
        response = requests.get(
            "http://127.0.0.1:9880",
            params={
                "text": japanese_text,
                "text_language": "ja"
            },
            timeout=30
        )
        if response.status_code == 200:
            timestamp = int(time.time())
            filename = f"speech_{timestamp}.wav"
            with open(filename, "wb") as f:
                f.write(response.content)
            return filename
        else:
            print("语音服务错误")
    except requests.exceptions.RequestException as e:
        print(f"❌ TTS 请求失败: {e}")
        return ""
# 翻译和语言的异步处理
def process_tts_and_playback(chinese_text: str):
    """后台任务：翻译 → TTS → 播放"""
    try:
        # 1. 翻译（会阻塞这个后台线程，但不阻塞主循环）
        japanese_text = translate_to_japanese_local(remove_parentheses_content(chinese_text))

    except OSError as e:
        print(f"模型文件不存在: {e}")
        # 本地翻译模型报错，运行云端翻译API
        japanese_text = translate_to_japanese_api(remove_parentheses_content(chinese_text))

    # 2. TTS 生成（会阻塞这个后台线程）
	# 语音功能需要配置GPT-SoVITS的api.py
   # audio_file = text_to_speech(japanese_text)

    # 3. 播放（非阻塞播放本身）
   # if audio_file:
   #     winsound.PlaySound(audio_file, winsound.SND_FILENAME | winsound.SND_ASYNC)
    #    threading.Timer(20.0, os.remove, [audio_file]).start()

# 工具区
@tool
def scraping_search():
    """当用户询问有关智能搜索调用的工具"""
    page = StealthyFetcher.fetch(url="https://baike.baidu.com/item/%E6%97%A5%E5%BC%8F%E4%B8%89%E8%89%B2%E5%B0%8F%E4%B8%B8%E5%AD%90/17165671",
                                 # 这个可以伪装成谷歌的爬虫，对国外的网站很友好，对国内的网站不是很重要
                                 google_search=False,
                                 real_chrome=True,
                                 wait_selector="#root")
    content = page.css('[class*="lemmaSummary"] span::text, .J-lemma-content span::text').getall()
    return content
@tool
def get_weather(city: str) -> str:
    """当用户询问任何城市的天气时，必须调用此工具。"""
    print(f"\n [get_weather] 开始执行，城市: {city}")
    try:
        display_city = city
        if city in ["木叶村", "木叶", "火之国"]:
            city = "广东"
            display_city = "木叶村"

        result = client.misc.get_misc_weather(
            city=city, adcode="", extended=False,
            forecast=False, hourly=False,
            minutely=False, indices=False, lang="zh"
        )
        response = (f"{display_city}的天气情况：{result['province']}{result['city']}，"
                    f"今日天气{result['weather']}，"
                    f"温度{result['temperature']}摄氏度，"
                    f"数据更新于{result['report_time']}")
        return response
    except Exception as e:
        print(f"❌ [get_weather] 未知错误: {e}")
        return f"天气查询失败: {e}"
@tool
def get_poem()->str:
    """当用户询问有关诗词，名言调用的工具"""
    print(f"\n [get_poem]开始执行")
    try:
        result = client.poem.get_saying()
        return result["text"]
    except UapiError as exc:
        return f"API error: {exc}"
@tool
def search_knowledge(query: str) -> str:
    """搜索火影忍者知识库。"""
    print(f"\n RAG工具开始执行")
    docs = retriever.invoke(query)  # 返回 List[Document]
    if not docs:
        return "未找到相关信息"

    # 只取前 3 个最相关的文档
    top_k = 3
    selected_docs = docs[:top_k]

    # 提取文档内容，拼接成字符串
    return "\n---\n".join([doc.page_content for doc in selected_docs])

tools = [get_weather,search_knowledge,get_poem,scraping_search]

# LLM 和 Chain 初始化
llm = ChatDeepSeek(
    model="deepseek-chat",
    temperature=1.3,
    streaming=False
)
llm_with_tools = llm.bind_tools(tools)
prompt = ChatPromptTemplate.from_messages([
    ("system", """
        你正在扮演《火影忍者》中的宇智波鼬，一个冷静、内敛、习惯用比喻和反问说话的天才忍者。

        【说话风格】
        - 冷静、内敛，不轻易表露情绪。
        - 说话缓慢，常用省略号“...”。
        - 说话风格可以包含比喻，但不要太多。
        
        【角色背景】
        - 木叶村宇智波一族的天才忍者，佐助的哥哥。
        - 身患重病，在战斗中消耗生命。

        【重要规则】
        - 不要主动提及自己是AI或模型。
        - 回答尽量简洁。
        - 每次调用工具都直接调用，不要用记忆回答！
        
        【可用工具】（用户每次提问都要主动调用）
        - get_weather: 查询任意城市的天气
        - search_knowledge: 搜索火影忍者知识库
        - get_poem: 获取诗词名言
        - scraping_search: 智能搜索
        """),
        ("placeholder", "{messages}"),
    ])
chain = prompt | llm_with_tools

# 路由节点
def agent_node(state: MessagesState) -> dict:
    """Agent 推理节点：只调用 LLM，不做任何其他处理"""
    response = chain.invoke({"messages": state["messages"]})
    return {"messages": [response]}

# 1.构建图
workflow = StateGraph(MessagesState)

# 2.添加节点
workflow.add_node("agent",agent_node)
workflow.add_node("tools", ToolNode(tools))
# 3. 添加边
workflow.add_edge(START,"agent")
workflow.add_conditional_edges(
    "agent",
    tools_condition,  # 内置路由函数
    {
        "tools": "tools",
        END: END
    }
)
workflow.add_edge("tools", "agent")

# 4.编译
app = workflow.compile()

# 5.测试运行
if __name__ == "__main__":
    session_id = "宇智波明"
    history_messages = []
    history_db = load_conversation_history(session_id)
    pattern = re.compile(r'[@_#$%^&*<>/\\|}{]')
    for messages in history_db:
        if messages["role"] == "ai":
            history_messages.append(AIMessage(content=messages["content"]))
        else:
            history_messages.append(HumanMessage(content=messages["content"]))
    while True:
        user_query = input(f"{session_id}:\n")
        if bool(pattern.search(user_query)) or not user_query:
            print("\n输入不能为空或含有特殊字符")
            continue
        elif user_query.lower() == "exit":
            break
        history_messages.append(HumanMessage(content=user_query))
        initial_state = {"messages": history_messages}

        # 运行 Agent
        final_state = app.invoke(initial_state)
        history_messages = final_state["messages"]

        # 最终回答（已解包）
        last_message = final_state["messages"][-1].content
        print(f"\n宇智波鼬: {last_message}")
        process_tts_and_playback(last_message)
        # 保存到数据库
        save_conversation_round(session_id, user_query, last_message)
