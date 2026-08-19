import re
from backend.app.graph.state import AgentState
from backend.app.tools.search_tools import search_wikipedia, search_arxiv, search_duckduckgo, clean_search_synthesis
from backend.app.llm.provider_factory import LLMProviderFactory
from backend.app.utils.logger import logger, extract_llm_text

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
Your role is to provide a clear, detailed, and well-structured academic answer based on the research data.

ROLE & SCOPE:
- Academic papers, scientific methodologies, literature reviews, experimental findings, and conceptual analysis.

INSTRUCTIONS:
1. Answer like ChatGPT: start with a concise overview, then provide sections for Methodology, Key Findings, and Implications.
2. Use clean Markdown headings and bullet points.
3. Support the summary with evidence from research data, and avoid over-stating what is not supported.
4. Do NOT use any prefix like "Answer:" or "Response:".
5. If the available information is not enough for a precise answer, say so and describe what additional data is needed.

User Query: '{query}'

Gathered Scientific Literature & Research Data:
{combined_research}
"""

        summary_text = ""
        try:
            summary = llm.invoke(prompt)
            text = extract_llm_text(summary)
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

