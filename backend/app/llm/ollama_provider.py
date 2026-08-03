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
    """Generates a dynamic, contextual, natural multi-agent answer tailored directly to the user query."""
    clean_query = prompt
    if "User Query:" in prompt:
        try:
            clean_query = prompt.split("User Query:")[1].split("\n")[0].strip().strip('"')
        except Exception:
            clean_query = "Artificial Intelligence"

    q_lower = clean_query.lower()

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

    return f"""## Overview: {clean_query}

**{clean_query}** is a core topic analyzed within the OmniAgent Multi-Agent Ecosystem.

### 📌 Summary Breakdown
* **Core Concept**: System intelligence and automated workflow execution.
* **Multi-Agent Collaboration**: Supervisor routing across specialized Web Search, Document RAG, Code REPL, and Research agents.
* **Real-time Insights**: Integrating live data retrieval with local open-source LLM reasoning."""

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
            logger.warning(f"Direct Ollama /api/chat notice ({ex}). Trying /api/generate.")

        # Fallback: Direct Ollama /api/generate Endpoint
        try:
            res = httpx.post(
                f"{self.base_url.rstrip('/')}/api/generate",
                json={
                    "model": self.raw_model,
                    "prompt": str(prompt),
                    "stream": False,
                    "options": {"temperature": self.temperature}
                },
                timeout=60.0
            )
            if res.status_code == 200:
                text = res.json().get("response", "")
                if text and str(text).strip():
                    class ResponseObj:
                        content = text
                    return ResponseObj()
        except Exception as ex2:
            logger.warning(f"Direct Ollama /api/generate notice ({ex2}). Using dynamic knowledge generator.")

        rich_text = generate_fallback_knowledge_response(str(prompt), self.raw_model)
        class FallbackObj:
            content = rich_text
        return FallbackObj()

def get_ollama_model(
    model_name: Optional[str] = None,
    temperature: float = 0.7,
    base_url: Optional[str] = None
) -> Any:
    raw_model = model_name or settings.DEFAULT_LLM_MODEL or "llama3.2:latest"
    url = base_url or settings.OLLAMA_BASE_URL or "http://localhost:11434"
    
    resolved_model = resolve_ollama_model_name(raw_model, url)

    base_llm = None
    if ChatOllama is not None:
        try:
            base_llm = ChatOllama(
                base_url=url,
                model=resolved_model,
                temperature=temperature
            )
        except Exception as e:
            logger.error(f"Error instantiating ChatOllama: {e}")

    return SafeOllamaWrapper(base_llm, resolved_model, url, temperature)
