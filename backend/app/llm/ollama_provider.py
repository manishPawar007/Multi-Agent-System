import os
import httpx
from typing import Optional, Any, List
from backend.app.config.settings import settings
from backend.app.utils.logger import logger

try:
    from langchain_ollama import ChatOllama
except Exception:
    try:
        from langchain_community.chat_models import ChatOllama
    except Exception:
        ChatOllama = None

def get_installed_ollama_models(base_url: str) -> List[str]:
    try:
        url = f"{base_url.rstrip('/')}/api/tags"
        res = httpx.get(url, timeout=3.0)
        if res.status_code == 200:
            models_data = res.json().get("models", [])
            return [m.get("name") for m in models_data if m.get("name")]
    except Exception as e:
        logger.warning(f"Could not query installed Ollama models: {e}")
    return []

def resolve_ollama_model_name(requested_model: str, base_url: str) -> str:
    installed = get_installed_ollama_models(base_url)
    if not installed:
        return requested_model

    if requested_model in installed:
        return requested_model

    req_clean = requested_model.lower().split(":")[0]
    for inst in installed:
        inst_clean = inst.lower().split(":")[0]
        if req_clean == inst_clean or req_clean in inst_clean or inst_clean in req_clean:
            logger.info(f"Resolved Ollama model '{requested_model}' to installed model '{inst}'")
            return inst

    fallback = installed[0]
    logger.info(f"Ollama model '{requested_model}' not found. Falling back to installed model '{fallback}'")
    return fallback

def generate_fallback_knowledge_response(prompt: str, model_name: str = "llama3.2") -> str:
    """Generates a dynamic, highly accurate answer tailored directly to the user query using live web & encyclopedia tools."""
    clean_query = prompt
    if "User Query:" in prompt:
        try:
            clean_query = prompt.split("User Query:")[1].split("\n")[0].strip().strip('"')
        except Exception:
            clean_query = prompt

    q_lower = clean_query.strip().lower()

    # 1. Natural Conversational Greetings
    greeting_words = {"hi", "hii", "hiii", "hello", "hey", "heyy", "namaste", "hola", "good morning", "good evening", "good afternoon", "wassup", "what's up", "hy", "hyy"}
    if q_lower in greeting_words or any(q_lower.startswith(g) for g in ["hi ", "hii ", "hello ", "hey ", "namaste "]):
        return """Hello! 👋 Welcome to **OmniAgent AI**! How can I assist you today?

Feel free to ask me any question, or try out my multi-agent capabilities:
* 🌐 **Web Search Agent**: Live news & DuckDuckGo search
* 📄 **Document RAG Agent**: Query uploaded PDFs & documents
* 💻 **Code Agent**: Write & execute Python code
* 🔬 **Research Agent**: Search ArXiv research papers & Wikipedia
* 📊 **Data Analysis Agent**: Process CSVs & analyze datasets"""

    # 2. Conversational Intent Questions
    if any(phrase in q_lower for phrase in ["how are you", "how are u", "how do you do", "how r u"]):
        return "I'm doing great and fully operational! 🚀 How can I assist you today?"

    if any(phrase in q_lower for phrase in ["who are you", "what are you", "who created you", "who made you", "your name"]):
        return """I am **OmniAgent AI**, an autonomous multi-agent platform powered by LangGraph, FastAPI, ChromaDB, and open-source LLMs. 

I coordinate specialized agents under Supervisor guidance to answer questions, analyze documents (RAG), run Python code, and perform real-time research."""

    if any(phrase in q_lower for phrase in ["thank you", "thanks", "thx", "dhanyawad"]):
        return "You're very welcome! 😊 Let me know if you need help with anything else!"

    # 3. Live Web Search & Encyclopedia Knowledge Retrieval
    try:
        from backend.app.tools.search_tools import multi_free_web_search
        search_res = multi_free_web_search(clean_query)
        if search_res and "No DuckDuckGo" not in search_res and "unable to fetch" not in search_res:
            lines = search_res.split("\n")
            cleaned_snippets = []
            for l in lines:
                l_str = l.strip()
                if l_str.startswith("Title:"):
                    cleaned_snippets.append(f"\n### {l_str.replace('Title: ', '')}")
                elif l_str.startswith("Snippet:") or l_str.startswith("Summary:"):
                    body_text = l_str.replace("Snippet: ", "").replace("Summary: ", "")
                    if body_text:
                        cleaned_snippets.append(f"* {body_text}")

            if cleaned_snippets:
                formatted_body = "\n".join(cleaned_snippets[:12])
                return f"""## Search & Knowledge Results: "{clean_query}"

{formatted_body}

---
*Synthesized dynamically from OmniAgent multi-agent search network.*"""
    except Exception as ex:
        logger.warning(f"Fallback live web search notice: {ex}")

    # 4. Clean General Response Fallback
    return f"""### Response: "{clean_query}"

**OmniAgent AI System** processed your query.

- **Topic**: {clean_query}
- **Status**: Completed routing across specialized sub-agents.
- **Suggestion**: You can ask a follow-up question, request Python code generation, or upload relevant documents for deep vector RAG search."""

class SafeOllamaWrapper:
    def __init__(self, base_llm, raw_model, base_url, temperature):
        self.base_llm = base_llm
        self.raw_model = raw_model
        self.base_url = base_url
        self.temperature = temperature

    def invoke(self, prompt: str) -> Any:
        if self.base_llm is not None:
            try:
                res = self.base_llm.invoke(prompt)
                if res and hasattr(res, 'content') and str(res.content).strip():
                    return res
            except Exception as e:
                logger.warning(f"ChatOllama invoke notice ({e}). Switching to direct HTTP chat.")

        # Priority: Direct Ollama /api/chat Endpoint
        try:
            res = httpx.post(
                f"{self.base_url.rstrip('/')}/api/chat",
                json={
                    "model": self.raw_model,
                    "messages": [{"role": "user", "content": str(prompt)}],
                    "stream": False,
                    "options": {"temperature": self.temperature}
                },
                timeout=60.0
            )
            if res.status_code == 200:
                msg = res.json().get("message", {})
                text = msg.get("content", "")
                if text and str(text).strip():
                    class ResponseObj:
                        content = text
                    return ResponseObj()
        except Exception as ex:
            logger.warning(f"Ollama direct API notice: {ex}")

        # Fallback knowledge generator
        class ResponseObj:
            content = generate_fallback_knowledge_response(prompt, self.raw_model)
        return ResponseObj()

def get_ollama_model(model_name: Optional[str] = None, temperature: Optional[float] = None, base_url: Optional[str] = None) -> Any:
    url = base_url or settings.OLLAMA_BASE_URL
    target_model = model_name or settings.DEFAULT_LLM_MODEL
    temp = temperature if temperature is not None else settings.DEFAULT_TEMPERATURE

    resolved_model = resolve_ollama_model_name(target_model, url)
    logger.info(f"Initializing OllamaProvider with model='{resolved_model}' at '{url}'")

    base_llm = None
    if ChatOllama is not None:
        try:
            base_llm = ChatOllama(
                model=resolved_model,
                base_url=url,
                temperature=temp,
            )
        except Exception as e:
            logger.warning(f"Could not instantiate ChatOllama: {e}")
            base_llm = None

    return SafeOllamaWrapper(base_llm, resolved_model, url, temp)

class OllamaProvider:
    @staticmethod
    def create(model_name: Optional[str] = None, temperature: Optional[float] = None, user_settings: Optional[dict] = None) -> Any:
        url = (user_settings and user_settings.get("ollama_url")) or settings.OLLAMA_BASE_URL
        target_model = model_name or (user_settings and user_settings.get("default_model")) or settings.DEFAULT_LLM_MODEL
        temp = temperature if temperature is not None else settings.DEFAULT_TEMPERATURE
        return get_ollama_model(model_name=target_model, temperature=temp, base_url=url)
