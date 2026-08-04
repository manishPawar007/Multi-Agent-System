from backend.app.graph.state import AgentState
from backend.app.tools.search_tools import multi_free_web_search, clean_search_synthesis
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
        prompt = f"""You are an expert AI Research Assistant. Provide a detailed, comprehensive, beautifully structured answer to the user query based on the search data below.

CRITICAL INSTRUCTIONS:
1. Provide a detailed, complete, and well-structured answer in clean Markdown. Use headings, bullet points, and clear explanations.
2. Do NOT use any prefix like "Answer:" or "Response:". Start directly with the core response.
3. Do NOT include raw search URLs, raw titles, or '=== Tavily' headers.

User Query: {query}

Search Data:
{raw_search}
"""

        summary = ""
        try:
            res = llm.invoke(prompt)
            text = res.content if hasattr(res, 'content') else str(res)
            if text and len(text.strip()) > 15 and not text.startswith("[Gemini API Error") and not text.startswith("[Gemini Provider]") and "API key not valid" not in text:
                summary = text.strip()
        except Exception as e:
            logger.warning(f"Web Search Agent LLM invocation notice: {e}")

        import re
        if summary:
            summary = re.sub(r"^\*{0,2}(Direct\s+)?Answer:\*{0,2}\s*", "", summary, flags=re.IGNORECASE).strip()

        # If LLM failed or returned raw/error text, synthesize cleanly using fallback extractor!
        if not summary or any(marker in summary for marker in ["=== Tavily", "=== Live Web", "Title:", "URL:", "Snippet:", "Relevance:", "[Gemini"]):
            summary = clean_search_synthesis(query, raw_search)

        if "agent_outputs" not in state or state["agent_outputs"] is None:
            state["agent_outputs"] = {}

        state["agent_outputs"]["web_search_agent"] = summary
        return state

