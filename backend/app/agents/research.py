from backend.app.graph.state import AgentState
from backend.app.tools.search_tools import search_wikipedia, search_arxiv, search_duckduckgo
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
        prompt = f"""You are an Expert Academic Research Agent.
User Query: '{query}'

Gathered Search & Literature Results:
{combined_research}

Instructions:
Synthesize a comprehensive, highly detailed academic summary covering:
- Key Research Concepts & Problem Statement
- Methodology & Technical Breakthroughs
- Important Findings & Performance Impact
- Future Implications

If specific papers were not named by the user, summarize foundational landmark research papers in the relevant AI/CS domain (e.g. Attention Is All You Need, Transformer Models, LLM Innovations)."""

        try:
            summary = llm.invoke(prompt)
            summary_text = summary.content if hasattr(summary, 'content') else str(summary)
        except Exception as e:
            logger.error(f"Research Agent LLM error: {e}")
            summary_text = combined_research[:1500]

        if "agent_outputs" not in state or state["agent_outputs"] is None:
            state["agent_outputs"] = {}

        state["agent_outputs"]["research_agent"] = summary_text
        return state
