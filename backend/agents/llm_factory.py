"""
LLM Factory
Returns the configured LangChain LLM based on environment settings.
Supported providers: groq, openai, anthropic
"""
from config import get_settings

settings = get_settings()


def get_llm(temperature: float = 0.1):
    """Return the configured LangChain chat model."""
    provider = settings.llm_provider.lower()
    model = settings.llm_model

    if provider == "groq":
        from langchain_groq import ChatGroq
        return ChatGroq(
            model=model,
            temperature=temperature,
            api_key=settings.groq_api_key,
        )

    elif provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        return ChatAnthropic(
            model=model,
            temperature=temperature,
            api_key=settings.anthropic_api_key,
        )

    else:
        # Default: OpenAI
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(
            model=model,
            temperature=temperature,
            api_key=settings.openai_api_key,
        )
