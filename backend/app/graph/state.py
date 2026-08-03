from typing import TypedDict, List, Dict, Any, Optional

class AgentState(TypedDict):
    input_query: str
    chat_id: str
    user_id: str
    provider: str
    model: str
    user_settings: Optional[Any]
    document_id: Optional[str]
    execution_plan: List[str]
    current_agent: str
    research_data: Optional[str]
    rag_context: Optional[str]
    document_summary: Optional[str]
    code_output: Optional[str]
    analysis_results: Optional[str]
    web_search_results: Optional[str]
    memory_context: Optional[str]
    agent_outputs: Dict[str, str]
    retry_counts: Dict[str, int]
    final_response: str
    error: Optional[str]
