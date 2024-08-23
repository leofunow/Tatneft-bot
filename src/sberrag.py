from langchain_community.chat_models import GigaChat
from langchain_community.embeddings import HuggingFaceEmbeddings
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.vectorstores import FAISS
from langchain.docstore.document import Document
import logging
logging.info("starting loading vector storage")

DOCS_FOLDER="/aiogram_files/"

docs = ["novye-tehnologii-pererabotki-tyazhelyh-neftey-i-prirodnyh-bitumov.pdf"]

chat = GigaChat(verify_ssl_certs=False, scope="GIGACHAT_API_PERS")
model_name = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
model_kwargs = {'device': 'cpu'}
encode_kwargs = {'normalize_embeddings': False}
embeddings = HuggingFaceEmbeddings(
    model_name=model_name,
    model_kwargs=model_kwargs,
    encode_kwargs=encode_kwargs
)
store = FAISS.from_documents(
    [Document(page_content="ошибка", metadata={"link": "error"})], embeddings)
text_splitter = RecursiveCharacterTextSplitter()


def read_pdf(file_name):
    reader = PdfReader(DOCS_FOLDER + file_name)
    pages = "\n\n".join([i.extract_text() for i in reader.pages])
    chunks = text_splitter.split_text(pages)
    chunks_docs = [Document(page_content=chunks[i], metadata={
                            "link": file_name}) for i in range(len(chunks))]
    store.add_documents(chunks_docs, embedding=embeddings)


for doc in docs:
    read_pdf(doc)

retriever = store.as_retriever()

logging.info("vector storage loaded!")
def answer_sbert(question):
    context = retriever.invoke(question)
    messages = [
        SystemMessage(
            content=f"Answer only in russian. Answer the questions based only on the following context (if question not in context, anwser 'Я не знаю'): {
                context}"
        ),
        HumanMessage(content=question),
    ]
    return {"answer": chat.invoke(messages).content,
            "context": context}
