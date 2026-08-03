from backend.app.graph.state import AgentState
from backend.app.rag.parser import DocumentParser
from backend.app.llm.provider_factory import LLMProviderFactory
from backend.app.utils.logger import logger

class DocumentAgent:
    def execute(self, state: AgentState) -> AgentState:
        query = state["input_query"]
        logger.info(f"Document Agent processing request: '{query}'")

        info = f"Document Agent ready. Processed document analysis and metadata generation request."
        state["document_summary"] = info

        if "agent_outputs" not in state or state["agent_outputs"] is None:
            state["agent_outputs"] = {}

        state["agent_outputs"]["document_agent"] = info
        return state
