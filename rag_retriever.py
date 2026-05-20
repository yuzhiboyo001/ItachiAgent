import os

from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.cross_encoders import HuggingFaceCrossEncoder
from langchain_community.vectorstores import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_classic.retrievers import EnsembleRetriever, ContextualCompressionRetriever
from langchain_classic.retrievers.document_compressors import CrossEncoderReranker
from langchain_classic.chains import create_retrieval_chain


def rag_retriever():
    # 1.文本加载
    # 知识库文件夹生成列表
    document_name = os.listdir("itachi_knowledge_base")
    # 做一个简单的去重
    unique_document = list(set(document_name))
    loading_file = []
    # 遍历知识库的文件夹列表里的文件
    for file_name in unique_document:
        # 拼接知识库文件夹名+列表里文件名的完整路径
        full_path = os.path.join("itachi_knowledge_base", file_name)
        # 只处理文件夹里后缀为txt格式的
        if file_name.endswith("txt"):
            # 每个文件都需要单独加载
            # 先初始化文档加载实例TextLoader,注意要加格式encoding="utf-8"
            loader = TextLoader(full_path, encoding="utf-8")
            # 然后运行加载
            loading = loader.load()
            # 把加载好的文档添加进列表
            loading_file.extend(loading)
    # 文档切块
    text_splitters = RecursiveCharacterTextSplitter(
        chunk_size=300,
        chunk_overlap=50,
        separators=["\n\n", "\n", "。", "！", "？", "；", " ", ""],
    )
    split_file = text_splitters.split_documents(loading_file)

    # 初始化embedding模型+向量化+存入向量数据库
    embeddings = HuggingFaceEmbeddings(
        model_name="BAAI/bge-small-zh-v1.5"
    )
    vector_db = Chroma.from_documents(
        split_file,
        embeddings,
        persist_directory="./chroma_db"
    )

    # 创建检索器（k=20：返回最相似的20个文本块，可根据需求调整）
    vector_retriever = vector_db.as_retriever(
        search_kwargs={
            "k": 20,
        })
    # 关键字检索
    bm25_retriever = BM25Retriever.from_documents(split_file)

    # 创建检索器的融合器(多路检索)
    ensemble_retriever = EnsembleRetriever(
        retrievers=[vector_retriever, bm25_retriever],
        weights=[0.5, 0.5]
    )

    # 重排序器
    reranker = CrossEncoderReranker(
        model=HuggingFaceCrossEncoder(model_name="BAAI/bge-reranker-base"),
        top_n=5
    )
    # 最终检索器
    retriever = ContextualCompressionRetriever(
        base_retriever=ensemble_retriever,
        base_compressor=reranker,
    )
    print("RAG知识检索加载完毕")
    return  retriever

