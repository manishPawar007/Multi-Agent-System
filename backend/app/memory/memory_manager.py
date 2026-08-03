from typing import List, Dict, Any

class MemoryManager:
    """Manages short-term conversation memory and long-term agent context."""
    def __init__(self):
        self.session_memories: Dict[str, List[Dict[str, str]]] = {}

    def add_message(self, session_id: str, role: str, content: str, agent_name: str = "supervisor"):
        if session_id not in self.session_memories:
            self.session_memories[session_id] = []
        self.session_memories[session_id].append({
            "role": role,
            "content": content,
            "agent_name": agent_name
        })

    def get_formatted_history(self, session_id: str, limit: int = 10) -> str:
        messages = self.session_memories.get(session_id, [])[-limit:]
        if not messages:
            return "No previous session conversation history."

        formatted = []
        for msg in messages:
            formatted.append(f"[{msg['role'].upper()} - {msg['agent_name']}]: {msg['content']}")
        return "\n".join(formatted)

    def summarize_memory(self, session_id: str) -> str:
        messages = self.session_memories.get(session_id, [])
        if not messages:
            return "Empty conversation session."
        return f"Session {session_id} has {len(messages)} interactions recorded."
