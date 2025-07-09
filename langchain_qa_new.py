from config import settings
from langchain_community.retrievers import AzureAISearchRetriever
from langchain_core.prompts import ChatPromptTemplate, PromptTemplate
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
import os
from langchain_openai import AzureChatOpenAI


llm = AzureChatOpenAI(
    azure_deployment=settings.chat_model,
    api_version="2024-12-01-preview",
    azure_endpoint=settings.openai_endpoint,
    temperature=0.,
    api_key=settings.openai_api_key
)

# 1. Azure Cognitive Search retriever 생성
def build_azure_search_retriever():
    retriever = AzureAISearchRetriever(
        service_name=settings.service_name,
        top_k=5,
        index_name=settings.index_name, 
        content_key="chunk", 
        api_key=settings.search_api_key
    )
    return retriever

condense_question_system_template = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)

condense_question_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", condense_question_system_template),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
    ]
)

azure_retriever = build_azure_search_retriever()

history_aware_retriever = create_history_aware_retriever(
    llm, azure_retriever, condense_question_prompt
)

def convert_streamlit_history_to_langchain(chat_history):
    """
    Streamlit의 st.session_state.messages (dict list) → LangChain 튜플 리스트로 변환
    """
    role_map = {"user": "human", "assistant": "assistant"}
    return [
        (role_map.get(msg["role"], msg["role"]), msg["content"])
        for msg in chat_history
        if "role" in msg and "content" in msg
    ]

# 2. Langchain 기반 QA 체인 생성

def create_langchain_qa_chain(retriever):
    system_prompt = (
    "You are an assistant for question-answering tasks. "
    "Use the following pieces of retrieved context to answer "
    "the question. If you don't know the answer, say that you "
    "don't know. Use ten sentences maximum and keep the "
    "answer concise."
    "\n\n"
    "{context}"
    "답변은 반드시 한국어로 작성한다. "
    "한 문장이 끝날 때마다 반드시 줄바꿈(Enter)을 한다."
    "Incident_ID: 인시던트(이상징후/장애)의 고유 ID입니다."
    "Registration_DateTime: 인시던트가 등록된 날짜와 시간입니다."
    "Service: 인시던트가 발생한 서비스명입니다."
    "Title_new: 인시던트의 요약 내용입니다."
    "Result: 인시던트 처리 결과 또는 해결 상태입니다."
    "Description: 인시던트에 대한 상세 설명입니다.(서비스명,현상,조치방안 등)"
    "Impact: 인시던트가 끼친 영향도 또는 피해 정도입니다."
    "Future_Plan: 향후 계획 또는 재발 방지 대책입니다."
    "Root_Cause: 인시던트의 근본 원인입니다."
    "답변은 원인, 영향도, 조치방안을 중점으로 작성한다."
    "이력에 대한 질문이 들어오면, 인시던트 ID, 서비스명을 기준으로 등록 날짜 및 시간, 요약 내용을 중심으로 답변한다."
)

    qa_prompt = ChatPromptTemplate.from_messages(
    [
        ("system", system_prompt),
        ("placeholder", "{chat_history}"),
        ("human", "{input}"),
    ]
)
    doc_prompt = PromptTemplate(
        input_variables=["Result", "Impact", "Future_Plan"], ##
        template=(
            "Title: {Result}\n"
            "Source: {Impact}\n"
            "Content: {Future_Plan}\n"
    )
)
    
    qa_chain = create_stuff_documents_chain(llm, qa_prompt, document_prompt=doc_prompt)
    convo_qa_chain = create_retrieval_chain(retriever, qa_chain)
    return convo_qa_chain

convo_qa_chain = create_langchain_qa_chain(azure_retriever)


