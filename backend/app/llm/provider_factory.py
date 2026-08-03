from typing import Optional, Any
from backend.app.config.settings import settings
from backend.app.llm.ollama_provider import get_ollama_model
from backend.app.llm.gemini_provider import get_gemini_model
from backend.app.utils.logger import logger

class LLMProviderFactory:
    @staticmethod
    def get_llm(
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: Optional[int] = None,
        user_settings: Optional[Any] = None
    ) -> Any:
        prov = (provider or (user_settings.default_provider if user_settings else None) or settings.DEFAULT_LLM_PROVIDER).lower()
        mod = model_name or (user_settings.default_model if user_settings else None) or settings.DEFAULT_LLM_MODEL
        temp = temperature if temperature is not None else (user_settings.temperature if user_settings else settings.DEFAULT_TEMPERATURE)
        tokens = max_tokens if max_tokens is not None else (user_settings.max_tokens if user_settings else settings.DEFAULT_MAX_TOKENS)

        logger.info(f"Initializing Free LLM Provider: [{prov}] Model: [{mod}] Temp: [{temp}]")

        try:
            if prov == "gemini" and (settings.ENABLE_CLOUD_GEMINI or (user_settings and getattr(user_settings, 'enable_cloud', False))):
                key = user_settings.gemini_key if user_settings and hasattr(user_settings, 'gemini_key') else settings.GEMINI_API_KEY
                return get_gemini_model(model_name=mod if "gemini" in mod else "gemini-1.5-flash", temperature=temp, max_tokens=tokens, api_key=key)
            else:
                # Default mode is ALWAYS local using Ollama
                url = user_settings.ollama_url if user_settings and hasattr(user_settings, 'ollama_url') else settings.OLLAMA_BASE_URL
                return get_ollama_model(model_name=mod, temperature=temp, base_url=url)
        except Exception as e:
            logger.error(f"Error creating LLM for provider {prov}: {str(e)}. Falling back to local Ollama.")
            return get_ollama_model(model_name=mod or "qwen3", temperature=temp)
