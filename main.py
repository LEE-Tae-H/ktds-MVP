from config import settings
from llm import LLM

llm = LLM(settings.openai_endpoint, settings.openai_api_key, settings.chat_model)

llm.get_openai_response()