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
        prov = (provider or (getattr(user_settings, 'default_provider', None) if user_settings else None) or settings.DEFAULT_LLM_PROVIDER).lower()
        mod = model_name or (getattr(user_settings, 'default_model', None) if user_settings else None) or settings.DEFAULT_LLM_MODEL
        temp = temperature if temperature is not None else (getattr(user_settings, 'temperature', None) if user_settings else settings.DEFAULT_TEMPERATURE) or settings.DEFAULT_TEMPERATURE
        tokens = max_tokens if max_tokens is not None else (getattr(user_settings, 'max_tokens', None) if user_settings else settings.DEFAULT_MAX_TOKENS) or settings.DEFAULT_MAX_TOKENS

        logger.info(f"LLM Provider: [{prov}] Model: [{mod}] Temp: [{temp}]")

        # --- Gemini (Google) ---
        if prov == "gemini" or "gemini" in (mod or ""):
            key = (getattr(user_settings, 'gemini_key', None) if user_settings else None) or settings.GEMINI_API_KEY
            if key:
                try:
                    gemini_model = mod if "gemini" in (mod or "") else "gemini-1.5-flash"
                    logger.info(f"Using Google Gemini: {gemini_model}")
                    return get_gemini_model(model_name=gemini_model, temperature=temp, max_tokens=tokens, api_key=key)
                except Exception as e:
                    logger.error(f"Gemini init error: {e}. Falling back to Ollama.")
            else:
                logger.warning("Gemini selected but GEMINI_API_KEY is not set. Falling back to Ollama.")

        # --- Ollama (local fallback) ---
        try:
            url = (getattr(user_settings, 'ollama_url', None) if user_settings else None) or settings.OLLAMA_BASE_URL
            ollama_model = mod if "gemini" not in (mod or "") else "llama3.2:latest"
            logger.info(f"Using local Ollama: {ollama_model} @ {url}")
            return get_ollama_model(model_name=ollama_model, temperature=temp, base_url=url)
        except Exception as e:
            logger.error(f"Ollama fallback error: {e}")
            return get_ollama_model(model_name="llama3.2:latest", temperature=temp)

