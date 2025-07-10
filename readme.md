# 🤖 장애조치 에이전트

## 📌 개요

**장애조치 에이전트**는 서비스 장애 발생 시, 사용자의 질문에 대해 **장애의 원인, 영향도, 조치방안**을 빠르고 명확하게 답변하여 신속한 대응을 지원하는 AI 기반 시스템입니다.  
사용자는 간단한 질문만으로도 복잡한 장애 상황에 대한 핵심 정보를 구조화된 형태로 받아볼 수 있습니다.

URL : https://user27-webapp-999-ffg3ahcnbrbzd7gx.swedencentral-01.azurewebsites.net/

---

## 🚀 주요 기능

✅ 장애 발생 원인 분석 및 설명  
✅ 장애의 영향도 및 영향 범위 안내  
✅ 재발 방지 및 해결 조치방안 제시  
✅ 대화 히스토리를 반영한 질문 재구성 지원  

---

## 🛠 사용 기술 스택

- Azure OpenAI  
- Azure Cognitive Search    
- Azure Storage Account     
- Azure AI Services    
- Azure Web App       
- LangChain   
- Streamlit    

## 🔗 서비스 플로우
 1. 사용자
 2. Streamlit UI (질문 입력)
 3. Langchain QA Chain (사용자 질문 -> 대화 히스토리 기반 질문 재구성) 
 4. Azure Congnitive Search (재구성된 질문을 바탕으로 문서 검색)
 5. Azure Open AI (LLM으로 답변 생성)
 6. 답변 출력

## 🎯 기대 효과

- 장애 대응 속도 향상
- 현업 부서의 신속한 의사결정 지원
- 지식 관리 및 문서화 자동화
- 재발 방지 및 품질 개선 기여

## 🎨 UI
![image](https://github.com/user-attachments/assets/fc2602ef-db83-4c8b-9b58-bcee8efe4120)
