from backend.app.graph.state import AgentState
from backend.app.tools.search_tools import multi_free_web_search, clean_search_synthesis
from backend.app.llm.provider_factory import LLMProviderFactory
from backend.app.utils.logger import logger, extract_llm_text

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
        prompt = f"""You are OmniAgent's Specialized Web Search Agent.
Your role is to answer user questions using the provided web search results.

ROLE & SCOPE:
- Real-time web data, current events, factual summaries, biographies, news, and current affairs.

INSTRUCTIONS:
1. Answer like ChatGPT: begin with a short direct summary, then expand with detailed context and supporting points.
2. Use clean Markdown headings, bullets, and concise paragraphs.
3. Only use the search data to support the answer; do not hallucinate additional facts.
4. Do NOT include raw search URLs, raw titles, or '=== Tavily' headers.
5. Do NOT use any prefix like "Answer:" or "Response:".
6. If the available search information is limited, clearly say so and provide the best answer possible from the data.

User Query: {query}

Live Web Search Data:
{raw_search}
"""

        summary = ""
        try:
            res = llm.invoke(prompt)
            text = extract_llm_text(res)
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

