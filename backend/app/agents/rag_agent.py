import re
from backend.app.graph.state import AgentState
from backend.app.rag.pipeline import RAGPipeline
from backend.app.llm.provider_factory import LLMProviderFactory
from backend.app.utils.logger import logger, extract_llm_text

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
        prompt = f"""You are OmniAgent's Specialized Document RAG Knowledge Agent.
Your role is to answer the user using only the retrieved document chunks from the uploaded PDF or document.

ROLE & SCOPE:
- Synthesize document insights, PDF summaries, page-specific explanations, and vector search evidence.

INSTRUCTIONS:
1. Answer like ChatGPT: begin with a clear direct response, then provide a detailed explanation using the document chunks.
2. Use clean Markdown headings, numbered sections, and bullet points.
3. Quote or reference the most relevant chunks when possible, and avoid making unsupported claims.
4. Do NOT use any prefix like "Answer:" or "Response:".
5. If the document does not contain enough information, say so honestly and explain what is missing.

User Query: "{query}"

Retrieved Document Chunks (ChromaDB Vector Store):
{context}
"""

        answer = ""
        try:
            res = llm.invoke(prompt)
            text = extract_llm_text(res)
            if text and len(text.strip()) > 20 and not text.startswith("[Gemini"):
                answer = text.strip()
        except Exception as e:
            logger.error(f"RAG Agent LLM error: {e}")

        if answer:
            answer = re.sub(r"^\*{0,2}Answer:\*{0,2}\s*", "", answer, flags=re.IGNORECASE).strip()

        if not answer:
            if context and context.strip():
                clean_chunks = []
                for chunk in context.split("\n\n"):
                    c_str = chunk.strip()
                    if c_str and not c_str.startswith("[Document Chunk"):
                        clean_chunks.append(f"* {c_str}")
                formatted_chunks = "\n".join(clean_chunks[:6]) if clean_chunks else context
                answer = f"### Document Context Insights\n\n{formatted_chunks}"
            else:
                answer = f"No uploaded document chunks were found for: **'{query}'**. Please upload a PDF file in the **Document Hub (RAG)** tab or select a document from the target dropdown to analyze your file."


        if "agent_outputs" not in state or state["agent_outputs"] is None:
            state["agent_outputs"] = {}

        state["agent_outputs"]["rag_agent"] = answer
        return state

