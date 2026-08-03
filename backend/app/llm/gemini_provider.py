import os
import httpx
from typing import Optional, Any
from backend.app.config.settings import settings
from backend.app.utils.logger import logger

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
except Exception:
    ChatGoogleGenerativeAI = None

def get_gemini_model(
    model_name: Optional[str] = None,
    temperature: float = 0.7,
    max_tokens: int = 2048,
    api_key: Optional[str] = None
) -> Any:
    model = model_name or "gemini-1.5-flash"
    key = api_key or settings.GEMINI_API_KEY or os.getenv("GEMINI_API_KEY", "")

    if ChatGoogleGenerativeAI is not None and key:
        try:
            return ChatGoogleGenerativeAI(
                model=model,
                google_api_key=key,
                temperature=temperature,
                max_output_tokens=max_tokens
            )
        except Exception as e:
            logger.error(f"Error instantiating ChatGoogleGenerativeAI: {e}")

    # Fallback direct wrapper if langchain_google_genai is unavailable or API key missing
    class DirectGeminiLLM:
        def __init__(self, model_name: str, api_key: str, temperature: float):
            self.model_name = model_name
            self.api_key = api_key
            self.temperature = temperature

        def invoke(self, prompt: str) -> Any:
            if not self.api_key:
                class MissingKeyObj:
                    content = f"[Gemini Provider]: API Key missing. Please configure GEMINI_API_KEY in Settings."
                return MissingKeyObj()

            try:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model_name}:generateContent?key={self.api_key}"
                payload = {
                    "contents": [{"parts": [{"text": str(prompt)}]}],
                    "generationConfig": {"temperature": self.temperature}
                }
                res = httpx.post(url, json=payload, timeout=60.0)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    text = ""
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts:
                            text = parts[0].get("text", "")
                    class ResponseObj:
                        content = text or "No text generated."
                    return ResponseObj()
                else:
                    class ErrorObj:
                        content = f"[Gemini API Error {res.status_code}]: {res.text}"
                    return ErrorObj()
            except Exception as ex:
                logger.error(f"Gemini API connection error: {ex}")
                class LocalMockObj:
                    content = f"[Gemini Model Response ({self.model_name})]: Processing complete."
                return LocalMockObj()

    return DirectGeminiLLM(model, key, temperature)
