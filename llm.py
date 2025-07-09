import os
import requests
from openai import AzureOpenAI
from datetime import datetime

class LLM:
    def __init__(self, openai_endpoint, openai_api_key, chat_model, search_endpoint, search_api_key, index_name):
        self.chat_client = AzureOpenAI(
            api_version="2024-12-01-preview",
            azure_endpoint=openai_endpoint,
            api_key=openai_api_key
        )
        self.chat_model = chat_model
        self.search_endpoint = search_endpoint
        self.search_api_key = search_api_key
        self.index_name = index_name

        # prompt.md 파일 읽어서 self.prompt_text에 저장
        prompt_path = os.path.join(os.path.dirname(__file__), "prompt.md")
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.prompt_text = f.read()

    def get_openai_response(self, query: str):
        try:
            rag_params = {
                "data_sources": [
                    {
                        "type": "azure_search",
                        "parameters": {
                            "endpoint": self.search_endpoint,
                            "index_name": self.index_name,
                            "authentication": {
                                "type": "api_key",
                                "key": self.search_api_key,
                            }
                        }
                    }
                ]
            }
            print("=== OpenAI 호출 system 메시지 ===")
            print(self.prompt_text)
            print("=== OpenAI 호출 user 메시지 ===")
            print(query)

            response = self.chat_client.chat.completions.create(
                model=self.chat_model,
                messages=[
                    {"role": "system", "content": f"{self.prompt_text}"},
                    {"role": "user", "content": query}
                ],
                max_tokens=1000,
                temperature=0.5,
                extra_body=rag_params
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"에러 발생: {e}"

    def _parse_month_filter(self, query: str):
        """
        쿼리에서 '2024년 1월', '2023년 10월' 등 월 단위 날짜를 추출해 Azure Search filter 쿼리로 변환
        """
        import re
        m = re.search(r'(\d{4})[년\-. ]+(\d{1,2})[월.]', query)
        if m:
            year = int(m.group(1))
            month = int(m.group(2))
            start = datetime(year, month, 1)
            if month == 12:
                end = datetime(year + 1, 1, 1)
            else:
                end = datetime(year, month + 1, 1)
            # Azure Search의 filter 쿼리(ISO8601)
            return f"occurred_at ge '{start.strftime('%Y-%m-%dT00:00:00Z')}' and occurred_at lt '{end.strftime('%Y-%m-%dT00:00:00Z')}'"
        return None

    def get_search_results(self, query: str, top: int = 20):
        """
        Azure Cognitive Search REST API를 직접 호출하여 결과를 리스트로 반환합니다.
        날짜 관련 질의(예: '2024년 1월', '2023년 10월')가 있으면 자동으로 filter를 추가합니다.
        """
        try:
            url = f"{self.search_endpoint}/indexes/{self.index_name}/docs/search?api-version=2023-11-01"
            headers = {
                "Content-Type": "application/json",
                "api-key": self.search_api_key
            }
            payload = {
                "search": query,
                "top": top
            }
            # 날짜 필터 자동 적용
            month_filter = self._parse_month_filter(query)
            if month_filter:
                payload["filter"] = month_filter
            resp = requests.post(url, headers=headers, json=payload)
            resp.raise_for_status()
            docs = resp.json().get("value", [])
            return docs
        except Exception as e:
            print(f"Azure Search 에러: {e}")
            return []

