from typing import Any, Dict, List, Optional

try:
    from langgraph.graph import StateGraph, END
    HAS_LANGGRAPH = True
except ImportError:
    StateGraph = None
    END = "__end__"
    HAS_LANGGRAPH = False

from backend.app.graph.state import AgentState
from backend.app.agents.supervisor import SupervisorAgent
from backend.app.agents.research import ResearchAgent
from backend.app.agents.rag_agent import RAGAgent
from backend.app.agents.document_agent import DocumentAgent
from backend.app.agents.code_agent import CodeAgent
from backend.app.agents.data_analysis import DataAnalysisAgent
from backend.app.agents.web_search_agent import WebSearchAgent
from backend.app.agents.memory_agent import MemoryAgent
from backend.app.utils.logger import logger

class MultiAgentGraph:
    def __init__(self):
        self.supervisor = SupervisorAgent()
        self.research_agent = ResearchAgent()
        self.rag_agent = RAGAgent()
        self.document_agent = DocumentAgent()
        self.code_agent = CodeAgent()
        self.data_analysis_agent = DataAnalysisAgent()
        self.web_search_agent = WebSearchAgent()
        self.memory_agent = MemoryAgent()

        self.agent_map = {
            "research_agent": self.research_agent,
            "rag_agent": self.rag_agent,
            "document_agent": self.document_agent,
            "code_agent": self.code_agent,
            "data_analysis_agent": self.data_analysis_agent,
            "web_search_agent": self.web_search_agent,
            "memory_agent": self.memory_agent,
        }

        if HAS_LANGGRAPH:
            self.graph = self._build_graph()
        else:
            logger.warning("langgraph package not found. Using native sequential agent runner fallback.")
            self.graph = None

    def _build_graph(self):
        workflow = StateGraph(AgentState)

        workflow.add_node("supervisor_plan", self.supervisor.plan_and_route)
        workflow.add_node("research_agent", self.research_agent.execute)
        workflow.add_node("rag_agent", self.rag_agent.execute)
        workflow.add_node("document_agent", self.document_agent.execute)
        workflow.add_node("code_agent", self.code_agent.execute)
        workflow.add_node("data_analysis_agent", self.data_analysis_agent.execute)
        workflow.add_node("web_search_agent", self.web_search_agent.execute)
        workflow.add_node("memory_agent", self.memory_agent.execute)
        workflow.add_node("supervisor_synthesize", self.supervisor.synthesize_response)

        workflow.set_entry_point("supervisor_plan")

        def route_next(state: AgentState) -> str:
            plan = state.get("execution_plan", [])
            completed = list(state.get("agent_outputs", {}).keys())

            for agent_name in plan:
                if agent_name not in completed and agent_name in self.agent_map:
                    state["current_agent"] = agent_name
                    return agent_name

            return "supervisor_synthesize"

        for node_name in ["research_agent", "rag_agent", "document_agent", "code_agent", "data_analysis_agent", "web_search_agent", "memory_agent"]:
            workflow.add_conditional_edges(
                node_name,
                route_next,
                {
                    "research_agent": "research_agent",
                    "rag_agent": "rag_agent",
                    "document_agent": "document_agent",
                    "code_agent": "code_agent",
                    "data_analysis_agent": "data_analysis_agent",
                    "web_search_agent": "web_search_agent",
                    "memory_agent": "memory_agent",
                    "supervisor_synthesize": "supervisor_synthesize",
                }
            )

        workflow.add_conditional_edges(
            "supervisor_plan",
            route_next,
            {
                "research_agent": "research_agent",
                "rag_agent": "rag_agent",
                "document_agent": "document_agent",
                "code_agent": "code_agent",
                "data_analysis_agent": "data_analysis_agent",
                "web_search_agent": "web_search_agent",
                "memory_agent": "memory_agent",
                "supervisor_synthesize": "supervisor_synthesize",
            }
        )

        workflow.add_edge("supervisor_synthesize", END)
        return workflow.compile()

    def _run_native_fallback(self, state: AgentState) -> AgentState:
        state = self.supervisor.plan_and_route(state)
        plan = state.get("execution_plan", [])

        for agent_name in plan:
            if agent_name in self.agent_map:
                try:
                    state = self.agent_map[agent_name].execute(state)
                except Exception as e:
                    logger.error(f"Error executing agent '{agent_name}': {str(e)}")

        state = self.supervisor.synthesize_response(state)
        return state

    def run(
        self,
        query: str,
        chat_id: str,
        user_id: str,
        provider: str = "ollama",
        model: str = "qwen3",
        user_settings: Any = None,
        document_id: Optional[str] = None
    ) -> AgentState:
        initial_state: AgentState = {
            "input_query": query,
            "chat_id": chat_id,
            "user_id": user_id,
            "provider": provider,
            "model": model,
            "user_settings": user_settings,
            "document_id": document_id,
            "execution_plan": [],
            "current_agent": "supervisor",
            "research_data": None,
            "rag_context": None,
            "document_summary": None,
            "code_output": None,
            "analysis_results": None,
            "web_search_results": None,
            "memory_context": None,
            "agent_outputs": {},
            "retry_counts": {},
            "final_response": "",
            "error": None
        }

        try:
            if HAS_LANGGRAPH and self.graph is not None:
                logger.info(f"Invoking LangGraph Multi-Agent Engine for query: '{query}' with document_id: '{document_id}'")
                output_state = self.graph.invoke(initial_state)
                return output_state
            else:
                logger.info(f"Invoking Native Multi-Agent Engine for query: '{query}' with document_id: '{document_id}'")
                return self._run_native_fallback(initial_state)
        except Exception as e:
            logger.error(f"Multi-agent graph processing exception: {str(e)}")
            return self._run_native_fallback(initial_state)

multi_agent_system = MultiAgentGraph()
