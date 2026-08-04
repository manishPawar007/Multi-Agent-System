import re
from backend.app.graph.state import AgentState
from backend.app.rag.parser import DocumentParser
from backend.app.llm.provider_factory import LLMProviderFactory
from backend.app.utils.logger import logger

def generate_fallback_document_analysis(query: str) -> str:
    return f"""### Document & Layout Analysis Overview

OmniAgent's Document Engine parses multi-modal file formats including PDF, DOCX, XLSX, PPTX, and TXT files using OCR layout extraction.

#### Supported Capabilities:
- **PDF Layout Extraction**: Text, headers, tables, and embedded images.
- **Office Documents (DOCX/XLSX)**: Paragraph hierarchies and structured data tables.
- **OCR Engine**: Optical character recognition for scanned PDFs and image-based documents.

**Query Breakdown:** {query}
"""

class DocumentAgent:
    def execute(self, state: AgentState) -> AgentState:
        query = state["input_query"]
        logger.info(f"Document Agent processing request: '{query}'")

        llm = LLMProviderFactory.get_llm(
            provider=state.get("provider"),
            model_name=state.get("model"),
            user_settings=state.get("user_settings")
        )
        prompt = f"""You are OmniAgent's Document Structure & Parsing Specialist.
Your sole duty is to explain document file formats, OCR text extraction, PDF layout parsing, and file conversion capabilities.

ROLE & SCOPE:
- PDF/DOCX/XLSX/PPTX parsing, OCR capabilities, document layout analysis, metadata extraction.

INSTRUCTIONS:
1. Provide a professional structural breakdown and document capability analysis in clean Markdown.
2. Do NOT use any prefix like "Answer:" or "Response:". Start directly with the document breakdown.

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
            info = generate_fallback_document_analysis(query)

        state["document_summary"] = info

        if "agent_outputs" not in state or state["agent_outputs"] is None:
            state["agent_outputs"] = {}

        state["agent_outputs"]["document_agent"] = info
        return state


