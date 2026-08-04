import re
from backend.app.graph.state import AgentState
from backend.app.rag.pipeline import RAGPipeline
from backend.app.llm.provider_factory import LLMProviderFactory
from backend.app.utils.logger import logger

class RAGAgent:
    def __init__(self, rag_pipeline: RAGPipeline = None):
        self.pipeline = rag_pipeline or RAGPipeline()

    def execute(self, state: AgentState) -> AgentState:
        query = state["input_query"]
        doc_id = state.get("document_id")
        user_id = state.get("user_id")

        logger.info(f"RAG Agent retrieving context for: '{query}' (target document_id='{doc_id}')")

        context = self.pipeline.retrieve_context(query, k=6, document_id=doc_id, user_id=user_id)
        state["rag_context"] = context

        llm = LLMProviderFactory.get_llm(
            provider=state.get("provider"),
            model_name=state.get("model"),
            user_settings=state.get("user_settings")
        )
        prompt = f"""You are an Expert Document RAG Knowledge & Summarization Agent.

User Instruction / Question: "{query}"

Retrieved PDF Document Chunks from ChromaDB Index:
{context}

CRITICAL INSTRUCTIONS:
1. Provide a comprehensive, highly accurate summary and detailed analysis based strictly on the retrieved PDF document chunks above.
2. Do NOT use any prefix like "Answer:" or "Response:". Start directly with the core document insights.
3. Highlight key points, main conclusions, methodologies, and core insights using clean Markdown bullet points and bold headings.
"""

        answer = ""
        try:
            res = llm.invoke(prompt)
            text = res.content if hasattr(res, 'content') else str(res)
            if text and len(text.strip()) > 20 and not text.startswith("[Gemini"):
                answer = text.strip()
        except Exception as e:
            logger.error(f"RAG Agent LLM error: {e}")

        if answer:
            answer = re.sub(r"^\*{0,2}Answer:\*{0,2}\s*", "", answer, flags=re.IGNORECASE).strip()

        if not answer:
            # Clean fallback formatting for retrieved chunks
            clean_chunks = []
            for chunk in (context or "").split("\n\n"):
                c_str = chunk.strip()
                if c_str and not c_str.startswith("[Document Chunk"):
                    clean_chunks.append(f"* {c_str}")
            formatted_chunks = "\n".join(clean_chunks[:6]) if clean_chunks else context
            answer = f"### Document Context Insights\n\n{formatted_chunks}"

        if "agent_outputs" not in state or state["agent_outputs"] is None:
            state["agent_outputs"] = {}

        state["agent_outputs"]["rag_agent"] = answer
        return state

