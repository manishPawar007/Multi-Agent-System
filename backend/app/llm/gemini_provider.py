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
    raw_model = (model_name or "gemini-3.6-flash").lower()
    if "pro" in raw_model:
        model = "gemini-3.6-pro"
    else:
        model = "gemini-3.6-flash"

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
                raise ValueError("GEMINI_API_KEY is not configured")

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
                    if text:
                        class ResponseObj:
                            content = text
                        return ResponseObj()
                    raise ValueError("Empty output text from Gemini API")
                else:
                    logger.error(f"Gemini API HTTP Error {res.status_code}: {res.text}")
                    raise ValueError(f"Gemini API error {res.status_code}")
            except Exception as ex:
                logger.error(f"Gemini API connection error: {ex}")
                raise ex

    return DirectGeminiLLM(model, key, temperature)

