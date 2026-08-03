from backend.app.graph.state import AgentState
from backend.app.memory.memory_manager import MemoryManager
from backend.app.utils.logger import logger

class MemoryAgent:
    def __init__(self, memory_manager: MemoryManager = None):
        self.memory_manager = memory_manager or MemoryManager()

    def execute(self, state: AgentState) -> AgentState:
        chat_id = state.get("chat_id", "default_session")
        logger.info(f"Memory Agent loading context for session: '{chat_id}'")

        history = self.memory_manager.get_formatted_history(chat_id)
        state["memory_context"] = history

        if "agent_outputs" not in state or state["agent_outputs"] is None:
            state["agent_outputs"] = {}

        state["agent_outputs"]["memory_agent"] = f"Relevant Session Memory:\n{history}"
        return state
