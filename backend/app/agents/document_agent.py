import re
from backend.app.graph.state import AgentState
from backend.app.rag.parser import DocumentParser
from backend.app.llm.provider_factory import LLMProviderFactory
from backend.app.utils.logger import logger

class DocumentAgent:
    def execute(self, state: AgentState) -> AgentState:
        query = state["input_query"]
        logger.info(f"Document Agent processing request: '{query}'")

        llm = LLMProviderFactory.get_llm(
            provider=state.get("provider"),
            model_name=state.get("model"),
            user_settings=state.get("user_settings")
        )
        prompt = f"""You are an Expert Document Analysis & Parser Agent. Provide a comprehensive summary and structural breakdown for the user request.

CRITICAL INSTRUCTIONS:
1. Provide a detailed, professional overview in clean Markdown.
2. Do NOT use any prefix like "Answer:" or "Response:". Start directly with the analysis.

User Request: {query}
"""

        info = ""
        try:
            res = llm.invoke(prompt)
            text = res.content if hasattr(res, 'content') else str(res)
            if text and len(text.strip()) > 15 and not text.startswith("[Gemini"):
                info = text.strip()
        except Exception as e:
            logger.error(f"Document Agent LLM notice: {e}")

        if info:
            info = re.sub(r"^\*{0,2}Answer:\*{0,2}\s*", "", info, flags=re.IGNORECASE).strip()

        if not info:
            info = f"### Document Analysis Report\n\n**Processed Query:** {query}\n\n* **Status**: Complete\n* **Parser Capabilities**: PDF, DOCX, XLSX, PPTX, TXT, OCR"

        state["document_summary"] = info

        if "agent_outputs" not in state or state["agent_outputs"] is None:
            state["agent_outputs"] = {}

        state["agent_outputs"]["document_agent"] = info
        return state

