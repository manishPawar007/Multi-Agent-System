import re
from backend.app.graph.state import AgentState
from backend.app.memory.memory_manager import MemoryManager
from backend.app.llm.provider_factory import LLMProviderFactory
from backend.app.utils.logger import logger

class MemoryAgent:
    def __init__(self, memory_manager: MemoryManager = None):
        self.memory_manager = memory_manager or MemoryManager()

    def execute(self, state: AgentState) -> AgentState:
        chat_id = state.get("chat_id", "default_session")
        query = state.get("input_query", "")
        logger.info(f"Memory Agent loading context for session: '{chat_id}'")

        history = self.memory_manager.get_formatted_history(chat_id)
        state["memory_context"] = history

        llm = LLMProviderFactory.get_llm(
            provider=state.get("provider"),
            model_name=state.get("model"),
            user_settings=state.get("user_settings")
        )
        prompt = f"""You are OmniAgent's Conversational Context & Memory Agent.
Your sole duty is to retrieve past conversation history, recall previous discussion points, and maintain conversational continuity.

ROLE & SCOPE:
- Recalling past user prompts, previous assistant responses, ongoing chat context.

INSTRUCTIONS:
1. Summarize relevant prior conversation points accurately and naturally in clean Markdown.
2. Do NOT use any prefix like "Answer:" or "Response:".

User Request: {query}
Session Memory History:
{history}
"""

        summary = ""
        try:
            res = llm.invoke(prompt)
            text = res.content if hasattr(res, 'content') else str(res)
            if text and len(text.strip()) > 15 and not text.startswith("[Gemini"):
                summary = text.strip()
        except Exception as e:
            logger.error(f"Memory Agent LLM notice: {e}")

        if summary:
            summary = re.sub(r"^\*{0,2}(Direct\s+)?Answer:\*{0,2}\s*", "", summary, flags=re.IGNORECASE).strip()

        if not summary:
            summary = f"### Session Memory Overview\n\n{history or 'No prior chat history found.'}"

        if "agent_outputs" not in state or state["agent_outputs"] is None:
            state["agent_outputs"] = {}

        state["agent_outputs"]["memory_agent"] = summary
        return state

