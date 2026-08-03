from backend.app.graph.state import AgentState
from backend.app.llm.provider_factory import LLMProviderFactory
from backend.app.llm.ollama_provider import generate_fallback_knowledge_response
from backend.app.utils.logger import logger

class SupervisorAgent:
    def __init__(self):
        pass

    def plan_and_route(self, state: AgentState) -> AgentState:
        query = state["input_query"].lower()
        provider = state.get("provider", "ollama")
        model = state.get("model", "llama3.2:latest")

        logger.info(f"Supervisor Agent analyzing query: '{state['input_query']}'")

        plan = []
        if any(w in query for w in ["research", "arxiv", "paper", "study", "wikipedia", "journal", "academic"]):
            plan.append("research_agent")
        if any(w in query for w in ["rag", "document", "file", "index", "vector", "stored", "uploaded", "summary", "summarize"]):
            plan.append("rag_agent")
        if any(w in query for w in ["parse", "pdf", "excel", "ocr", "metadata", "extract"]):
            plan.append("document_agent")
        if any(w in query for w in ["code", "python", "java", "javascript", "sql", "bug", "html", "css", "refactor", "script", "function", "program"]):
            plan.append("code_agent")
        if any(w in query for w in ["csv", "data", "chart", "statistics", "trend", "dataframe", "table", "mean", "sum", "math", "calculate"]):
            plan.append("data_analysis_agent")
        if any(w in query for w in ["search", "web", "latest", "news", "duckduckgo", "github", "url", "what is", "who is", "explain"]):
            plan.append("web_search_agent")
        if any(w in query for w in ["memory", "remember", "history", "previous"]):
            plan.append("memory_agent")

        # Fallback to web search and RAG if query is broad
        if not plan:
            plan = ["web_search_agent", "rag_agent"]

        state["execution_plan"] = plan
        state["current_agent"] = plan[0]
        logger.info(f"Supervisor Execution Plan created: {plan}")

        return state

    def synthesize_response(self, state: AgentState) -> AgentState:
        provider = state.get("provider", "ollama")
        model = state.get("model", "llama3.2:latest")
        user_settings = state.get("user_settings")
        llm = LLMProviderFactory.get_llm(provider=provider, model_name=model, user_settings=user_settings)

        query = state["input_query"]
        agent_outputs = state.get("agent_outputs", {})

        collected_info = []
        for agent_name, output in agent_outputs.items():
            if output and str(output).strip():
                collected_info.append(f"=== Insights from [{agent_name.upper()}] ===\n{output}\n")

        context = "\n\n".join(collected_info) if collected_info else "No sub-agent insights available."

        prompt = f"""You are the Lead Supervisor AI of OmniAgent AI, an advanced LangGraph Multi-Agent Ecosystem.

User Query: "{query}"

Sub-Agent Insights & Execution Data:
{context}

CRITICAL RESPONSE GUIDELINES MATCHING TOP MULTI-AGENT SYSTEMS (CrewAI / AutoGen / LangGraph):
1. Synthesize a direct, natural, highly intelligent answer tailored specifically to the exact intent of the user query: "{query}".
2. Adapt your tone and response format dynamically:
   - For simple/direct questions (e.g. "what is AI?", "what is ML?"), provide a clean, clear, well-structured explanation matching the query.
   - For complex multi-step queries (coding, document retrieval, research synthesis), provide comprehensive breakdowns with section headers, examples, code blocks, or mathematical formulas as relevant.
3. Use clean GitHub-style Markdown (headings, bullet points, bold key terms, fenced code blocks).
4. If sub-agent insights are available from Web Search, Document RAG, Code REPL, or Research agents, seamlessly integrate their findings into your response and cite them naturally.

Synthesize the final answer for the user:"""

        try:
            response = llm.invoke(prompt)
            final_text = response.content if hasattr(response, 'content') else str(response)
            state["final_response"] = final_text
        except Exception as e:
            logger.error(f"Supervisor synthesis fallback: {str(e)}")
            state["final_response"] = generate_fallback_knowledge_response(query, model)

        return state
