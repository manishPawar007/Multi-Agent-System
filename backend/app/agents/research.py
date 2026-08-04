import re
from backend.app.graph.state import AgentState
from backend.app.tools.search_tools import search_wikipedia, search_arxiv, search_duckduckgo, clean_search_synthesis
from backend.app.llm.provider_factory import LLMProviderFactory
from backend.app.utils.logger import logger

class ResearchAgent:
    def execute(self, state: AgentState) -> AgentState:
        query = state["input_query"]
        logger.info(f"Research Agent executing research for query: '{query}'")

        # Refine query for search tools if query is generic
        search_term = query
        if any(g in query.lower() for g in ["summarize the research paper", "summarize paper", "research paper summary"]):
            search_term = "transformer neural network architecture deep learning"

        # 1. Query Wikipedia
        wiki_res = search_wikipedia(search_term)

        # 2. Query Arxiv
        arxiv_res = search_arxiv(search_term)

        # 3. Query DuckDuckGo
        ddg_res = search_duckduckgo(search_term)

        combined_research = f"{wiki_res}\n\n{arxiv_res}\n\n{ddg_res}"
        state["research_data"] = combined_research

        # Summarize findings with LLM
        llm = LLMProviderFactory.get_llm(
            provider=state.get("provider"),
            model_name=state.get("model"),
            user_settings=state.get("user_settings")
        )
        prompt = f"""You are OmniAgent's Academic Research Agent.
Your sole duty is to analyze scientific literature, ArXiv research papers, Wikipedia encyclopedia data, and academic concepts.

ROLE & SCOPE:
- Academic papers, scientific methodologies, literature reviews, foundational research concepts.

INSTRUCTIONS:
1. Provide an in-depth academic summary formatted in clean Markdown (covering Overview, Methodology, Key Findings, and Future Implications).
2. Do NOT use any prefix like "Answer:" or "Response:". Start directly with the research synthesis.

User Query: '{query}'

Gathered Scientific Literature & Research Data:
{combined_research}
"""

        summary_text = ""
        try:
            summary = llm.invoke(prompt)
            text = summary.content if hasattr(summary, 'content') else str(summary)
            if text and len(text.strip()) > 20 and not text.startswith("[Gemini"):
                summary_text = text.strip()
        except Exception as e:
            logger.error(f"Research Agent LLM notice: {e}")

        # Strip any 'Answer:' prefix
        if summary_text:
            summary_text = re.sub(r"^\*{0,2}Answer:\*{0,2}\s*", "", summary_text, flags=re.IGNORECASE).strip()

        # Fallback to clean synthesis if LLM failed
        if not summary_text or any(m in summary_text for m in ["=== Tavily", "Title:", "URL:", "[Gemini"]):
            summary_text = clean_search_synthesis(query, combined_research)

        if "agent_outputs" not in state or state["agent_outputs"] is None:
            state["agent_outputs"] = {}

        state["agent_outputs"]["research_agent"] = summary_text
        return state

