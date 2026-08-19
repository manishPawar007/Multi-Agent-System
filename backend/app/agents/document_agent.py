import re
from backend.app.graph.state import AgentState
from backend.app.rag.parser import DocumentParser
from backend.app.llm.provider_factory import LLMProviderFactory
from backend.app.utils.logger import logger, extract_llm_text

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
Your role is to explain document file formats, OCR parsing, layout extraction, and how to analyze documents effectively.

ROLE & SCOPE:
- PDF/DOCX/XLSX/PPTX parsing, OCR, layout analysis, metadata extraction, and document workflow guidance.

INSTRUCTIONS:
1. Answer like ChatGPT: begin with a short direct summary, then provide a detailed explanation with headings and examples.
2. Make the response easy to understand for non-technical users while preserving technical accuracy.
3. Do NOT use any prefix like "Answer:" or "Response:".
4. If the request is about a feature or workflow, explain the correct steps clearly.

User Request: {query}
"""

        info = ""
        try:
            res = llm.invoke(prompt)
            text = extract_llm_text(res)
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


