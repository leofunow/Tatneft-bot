from langchain_community.chat_models import GigaChat
from langchain_community.embeddings import HuggingFaceEmbeddings
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langchain.retrievers import EnsembleRetriever
import re
from langchain.docstore.document import Document
import pickle
import logging
from os import getenv
import os
import urllib
import json

from aiogram import Bot, Dispatcher, html
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

TOKEN = getenv("BOT_TOKEN")


logging.info("starting loading vector storage")

DOCS_FOLDER="/aiogram_files/"

pattern = re.compile(r'(?<=[а-я])Т(?=[а-я])')


# docs = ["o_vozmozhnosti_izvlecheniya_metallov_iz_vysokovyazkih_neftey_rossiyskih.pdf", "ob_intensifikatsii_dobychi_nefti_na_pozdney_stadii_razrabotki_almetievskoy.pdf", "statisticheskiy-analiz-kachestva-trudnoizvlekaemyh-neftey.pdf"]

chat = GigaChat(verify_ssl_certs=False, scope="GIGACHAT_API_PERS")
model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs,
    cache_folder="/aiogram_cache/embeddings",
)

def save_faiss():
    store.save_local("/aiogram_cache/faiss_index")

def save_bm(retriever_to_safe, docs_list):
    with open('/aiogram_cache/bm_retriever/bm25_retriever.pkl', 'wb') as f:
        pickle.dump(retriever_to_safe, f)

    with open('/aiogram_cache/bm_retriever/docs_list.pkl', 'wb') as f:
        pickle.dump(docs_list, f)


try:
    store = FAISS.load_local("/aiogram_cache/faiss_index", embeddings=embeddings, allow_dangerous_deserialization=True)
except Exception as e:
    store = FAISS.from_documents(
    [Document(page_content="ошибка", metadata={"link": "error"})], embeddings)
    logging.info(e)

if not os.path.exists("/aiogram_cache/bm_retriever"):
    os.makedirs("/aiogram_cache/bm_retriever")

bm_retriever = BM25Retriever.from_documents([Document(page_content="ошибка", metadata={"link": "error"})])
with open('/aiogram_cache/bm_retriever/bm25_retriever.pkl', 'wb') as f:
    pickle.dump(bm_retriever, f)
docs_list = []
with open('/aiogram_cache/bm_retriever/docs_list.pkl', 'wb') as f:
    pickle.dump(docs_list, f)


try:
    with open('/aiogram_cache/bm_retriever/bm25_retriever.pkl', 'rb') as f:
        bm_retriever = pickle.load(f)

    with open('/aiogram_cache/bm_retriever/docs_list.pkl', 'rb') as f:
        docs_list = pickle.load(f)
except Exception as e:
    bm_retriever = BM25Retriever.from_documents([Document(page_content="ошибка", metadata={"link": "error"})])
    with open('/aiogram_cache/bm_retriever/bm25_retriever.pkl', 'wb') as f:
        pickle.dump(bm_retriever, f)
    docs_list = []
    with open('/aiogram_cache/bm_retriever/docs_list.pkl', 'wb') as f:
        pickle.dump(docs_list, f)

ensemble_retriever = EnsembleRetriever(
        retrievers=[bm_retriever, store.as_retriever()],
         weights=[0.4, 0.6],
    )


# load_faiss()
# store = store2
text_splitter = RecursiveCharacterTextSplitter(separators="/n /n")


def read_pdf(file_name):
    global bm_retriever
    global docs_list
    global ensemble_retriever
    reader = PyPDFLoader(DOCS_FOLDER + file_name)
    pages = reader.load_and_split(text_splitter=text_splitter)
    for i in range(len(pages)):
        tmp = pages[i].page_content
        tmp = tmp.replace(' -\n', '')
        tmp = tmp.replace('-\n', '')
        tmp = tmp.replace('Т\n', '')
        tmp = tmp.replace('________________', '')
        tmp = pattern.sub('', tmp)
        pages[i].page_content = tmp
        

    chunks_docs = [Document(page_content=pages[i].page_content, metadata={
                            "link": file_name}) for i in range(len(pages))]
    
    
    store.add_documents(chunks_docs, embedding=embeddings)
    docs_list = docs_list + chunks_docs
    bm_retriever = BM25Retriever.from_documents(docs_list)
    ensemble_retriever = EnsembleRetriever(
        retrievers=[bm_retriever, store.as_retriever()], weights=[0.4, 0.6],
    )
    save_faiss()
    save_bm(bm_retriever, docs_list)


retriever = store.as_retriever()

logging.info("vector storage loaded!")
def answer_sbert(question: str):
    with open('keywords.json', 'r', encoding='utf-8') as json_data:
        keywords = json.load(json_data)
    for key in keywords.keys():
        question = question.replace(key, f"{key}({keywords[key]})")
        # question = question.replace(key.lower(), f"{key}({keywords[key]})")
    context = ensemble_retriever.invoke(question)[:4]
    messages = [
        SystemMessage(
            content=f"Ты - помощник по поиску информации, который использует извлеченные данные для генерации ответов на вопросы. Тебе предоставлен текстовый отрывок, в котором может содержаться информация, необходимая для ответа на вопрос. Если ты найдешь нужную информацию в тексте, используй ее для составления ответа. Если необходимой информации в тексте нет, просто ответь (Не знаю)./nКонтекст: {context}"
        ),
        HumanMessage(content=question),
    ]
    return {"answer": chat.invoke(messages).content,
            "context": context}



async def add_document(file_id, name):
    bot = Bot(token=TOKEN, default=DefaultBotProperties(
        parse_mode=ParseMode.HTML))
    file = await bot.get_file(file_id)
    fi = file.file_path
    urllib.request.urlretrieve(f'https://api.telegram.org/file/bot{TOKEN}/{fi}',f'{DOCS_FOLDER}{name}')
    read_pdf(name)
    # await bot.send_message(msg.from_user.id, 'Файл успешно сохранён')
    # await file.download(destination=DOCS_FOLDER + file.file_path)