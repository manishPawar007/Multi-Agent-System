from backend.app.graph.state import AgentState
from backend.app.rag.pipeline import RAGPipeline
from backend.app.llm.provider_factory import LLMProviderFactory
from backend.app.utils.logger import logger

class RAGAgent:
    def __init__(self, rag_pipeline: RAGPipeline = None):
        self.pipeline = rag_pipeline or RAGPipeline()

    def execute(self, state: AgentState) -> AgentState:
        query = state["input_query"]
        logger.info(f"RAG Agent retrieving context for: '{query}'")

        context = self.pipeline.retrieve_context(query, k=4)
        state["rag_context"] = context

        llm = LLMProviderFactory.get_llm(
            provider=state.get("provider"),
            model_name=state.get("model"),
            user_settings=state.get("user_settings")
        )
        prompt = f"""You are a Document RAG Knowledge Agent.
User Question: {query}

Retrieved Document Chunks from ChromaDB Index:
{context}

Instructions:
1. If relevant document chunks are present in the context above, use them to provide a detailed, accurate answer.
2. If NO relevant document chunks are found (or no files have been uploaded yet):
   - Answer the question directly using your comprehensive knowledge base.
   - Mention that custom document chunks were not matched in the ChromaDB vector store, and remind the user that they can upload PDFs/documents in the 'Document Hub (RAG)' tab for custom file QA.
"""

        try:
            res = llm.invoke(prompt)
            answer = res.content if hasattr(res, 'content') else str(res)
        except Exception as e:
            logger.error(f"RAG Agent LLM error: {e}")
            answer = f"RAG Retrieval Context:\n{context}"

        if "agent_outputs" not in state or state["agent_outputs"] is None:
            state["agent_outputs"] = {}

        state["agent_outputs"]["rag_agent"] = answer
        return state
