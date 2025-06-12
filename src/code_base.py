import os
from dotenv import load_dotenv
from langchain_community.document_loaders import (
    PyPDFLoader,
    UnstructuredWordDocumentLoader,
    UnstructuredExcelLoader,
    UnstructuredCSVLoader,
    TextLoader,
)
from langchain_text_splitters import TokenTextSplitter
from langchain.docstore.document import Document
from langchain_openai import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings

from langchain.memory import ConversationBufferMemory
from langchain.chains import ConversationalRetrievalChain




load_dotenv()
HUGFACE_API = os.getenv('HG_API')
DEEPSEEK_TOKEN = os.getenv('DSEEK_API')


def file_processor(file_path):
    # load file_doc
    ext = os.path.splitext(file_path)[1].lower()
    
    if ext == ".pdf":
        loader = PyPDFLoader(file_path)
    elif ext == ".docx":
        loader = UnstructuredWordDocumentLoader(file_path)
    elif ext in [".xls", ".xlsx"]:
        loader = UnstructuredExcelLoader(file_path)
    elif ext == ".csv":
        loader = UnstructuredCSVLoader(file_path)
    elif ext == ".txt":
        loader = TextLoader(file_path, encoding='utf-8')
    else:
        raise ValueError(f"Unsupported file extension: {ext}")
    
    file = loader.load()
    
    # extract all page content as str
    all_files = ""
    for page in file:
        all_files += page.page_content
    
    # split and chunk for question and answer generation   
    text_splitter_q = TokenTextSplitter(chunk_size=4000, chunk_overlap=200)
    texts_chunk_q = text_splitter_q.split_text(all_files)
    
    
    # convert chunks into a doc file
    doc_maker_q = [Document(page_content=pag) for pag in texts_chunk_q]
    
    return doc_maker_q


# load model and give result
def model_pipeline(doc_gen, prompt):
    
    # instatiate llm model
    llm = ChatOpenAI(
        openai_api_base="https://openrouter.ai/api/v1",
        openai_api_key=DEEPSEEK_TOKEN,
        model_name='deepseek/deepseek-r1:free',
        temperature=0.6,
        max_completion_tokens= 140000,
        streaming= True,
        )
    
    # prompt templating
    question_prompt = PromptTemplate.from_template("""
                                                   Your goal is to help answer {questions} from the documentations provided.
                                                   Ensure important information are not omitted.
                                                   If the question is irrelevant to the documentation, 
                                                   please reply with 'question not relevant to the document'.
                                                   Ensure to check your memory for conversational chain.
                                                   """)
    

    
    # vector embedding of doc
    model_embed = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    vector_store = FAISS.from_documents(doc_gen, model_embed)
    
    
    # Setup memory
    memory = ConversationBufferMemory(
        memory_key="chat_history",  # default is 'chat_history'
        return_messages=True,
        output_key='answer'
    )

# Build ConversationalRetrievalChain
    qa = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=vector_store.as_retriever(),
        memory=memory,
        return_source_documents=True,
        output_key="answer" 
    )

    result = qa.invoke({"question": question_prompt.format(questions=prompt)})

    
    return result["answer"]

