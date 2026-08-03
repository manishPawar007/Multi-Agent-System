from backend.app.graph.state import AgentState
from backend.app.tools.search_tools import multi_free_web_search
from backend.app.llm.provider_factory import LLMProviderFactory
from backend.app.utils.logger import logger

class WebSearchAgent:
    def execute(self, state: AgentState) -> AgentState:
        query = state["input_query"]
        logger.info(f"Web Search Agent searching free search APIs for query: '{query}'")

        raw_search = multi_free_web_search(query)
        state["web_search_results"] = raw_search

        llm = LLMProviderFactory.get_llm(
            provider=state.get("provider"),
            model_name=state.get("model"),
            user_settings=state.get("user_settings")
        )
        prompt = f"""Synthesize and summarize these search results from free open sources (DuckDuckGo, Wikipedia, Arxiv, GitHub).

User Query: {query}

Raw Search Results:
{raw_search}
"""

        try:
            res = llm.invoke(prompt)
            summary = res.content if hasattr(res, 'content') else str(res)
        except Exception:
            summary = raw_search

        if "agent_outputs" not in state or state["agent_outputs"] is None:
            state["agent_outputs"] = {}

        state["agent_outputs"]["web_search_agent"] = summary
        return state
