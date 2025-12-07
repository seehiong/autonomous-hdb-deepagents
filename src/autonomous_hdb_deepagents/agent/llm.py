import os
from langchain_openai import ChatOpenAI

# Shared LLM instance for the whole package
llm = ChatOpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    base_url="https://openrouter.ai/api/v1",
    model="amazon/nova-2-lite-v1:free",
    temperature=0
)
