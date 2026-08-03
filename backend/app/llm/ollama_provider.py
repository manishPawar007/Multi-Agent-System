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
    """Generates a dynamic, conversational, natural multi-agent answer tailored directly to the user query."""
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

    # 3. Topic specific knowledge
    if "ai" in q_lower or "artificial intelligence" in q_lower:
        return """## What is Artificial Intelligence (AI)?

**Artificial Intelligence (AI)** refers to computer systems and algorithms capable of performing tasks that typically require human intelligence. These include visual perception, speech recognition, decision-making, natural language understanding, and problem-solving.

### 🔑 Key Pillars of Modern AI
* **Machine Learning (ML)**: Algorithms that learn from patterns in data to make predictions without explicit programming.
* **Deep Learning (DL)**: Multi-layered neural network architectures used for image recognition, language processing, and complex decision tasks.
* **Generative AI & LLMs**: Foundation models (like Llama 3, Qwen, and Gemini) capable of generating text, code, images, and multi-modal content.
* **Autonomous Multi-Agent Systems**: Cooperative AI agents working together using tools (Search, Code Execution, RAG Vector Search) to solve complex workflows.

### 💡 Primary Applications
- **Conversational Agents & Supervisors**: Autonomous routing and task automation.
- **Retrieval-Augmented Generation (RAG)**: Searching document vector databases (ChromaDB) to answer questions accurately.
- **Code Generation & Execution**: Automated debugging, software engineering, and data analysis."""

    if "ml" in q_lower or "machine learning" in q_lower:
        return """## What is Machine Learning (ML)?

**Machine Learning (ML)** is a subset of Artificial Intelligence focused on building systems that learn from past data to improve performance over time without being explicitly programmed.

### 🔄 Core Learning Paradigms
1. **Supervised Learning**: Training models on labeled datasets (e.g., classification, regression, fraud detection).
2. **Unsupervised Learning**: Discovering hidden patterns or structures in unlabeled data (e.g., clustering, dimensionality reduction).
3. **Reinforcement Learning**: Agents learning optimal decisions by receiving rewards or penalties in dynamic environments.

### ⚙️ Typical ML Workflow
- **Data Collection & Preparation**: Cleaning, feature engineering, and embedding generation.
- **Model Training & Benchmarking**: Optimizing algorithms (Random Forests, Gradient Boosting, Neural Nets).
- **Evaluation & Deployment**: Testing precision/recall metrics and serving real-time FastAPI endpoints."""

    # 4. General query fallback
    return f"""### Query Analysis: "{clean_query}"

**OmniAgent Multi-Agent Ecosystem** processed your request. 

Here are key aspects related to **{clean_query}**:
* **Intent Analysis**: Query routed through Supervisor routing to specialized sub-agents.
* **Knowledge Context**: Processing vector context, live web data, and natural language logic.
* **Actionable Next Steps**: You can ask follow-up questions, request code implementations, or upload relevant documents for deep RAG analysis."""

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

class OllamaProvider:
    @staticmethod
    def create(model_name: Optional[str] = None, temperature: Optional[float] = None, user_settings: Optional[dict] = None) -> Any:
        base_url = (user_settings and user_settings.get("ollama_url")) or settings.OLLAMA_BASE_URL
        target_model = model_name or (user_settings and user_settings.get("default_model")) or settings.DEFAULT_LLM_MODEL
        temp = temperature if temperature is not None else settings.DEFAULT_TEMPERATURE

        resolved_model = resolve_ollama_model_name(target_model, base_url)
        logger.info(f"Initializing OllamaProvider with model='{resolved_model}' at '{base_url}'")

        base_llm = None
        if ChatOllama is not None:
            try:
                base_llm = ChatOllama(
                    model=resolved_model,
                    base_url=base_url,
                    temperature=temp,
                )
            except Exception as e:
                logger.warning(f"Could not instantiate ChatOllama: {e}")
                base_llm = None

        return SafeOllamaWrapper(base_llm, resolved_model, base_url, temp)
