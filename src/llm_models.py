from langchain_google_genai import ChatGoogleGenerativeAI
from config import Settings

def get_language_model(llm_settings: Settings):
    gemini_llm = ChatGoogleGenerativeAI(model = llm_settings.gemini_chat_model,
                                        api_key = llm_settings.gemini_api_key,
                                        max_retries = llm_settings.max_llm_retries,
                                        )

    return gemini_llm