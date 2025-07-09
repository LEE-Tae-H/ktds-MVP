import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    openai_endpoint = os.getenv("OPENAI_ENDPOINT")
    openai_api_key = os.getenv("OPENAI_API_KEY")
    chat_model = os.getenv("CHAT_MODEL")
    search_endpoint = os.getenv("SEARCH_ENDPOINT")
    search_api_key = os.getenv("SEARCH_API_KEY")
    index_name = os.getenv("INDEX_NAME")
    service_name = os.getenv("SEARCH_SERVICE_NAME")

    def load_system_prompt():
        with open("경로", "r", encoding="utf-8") as f:
            return f.read()
    
settings = Settings()