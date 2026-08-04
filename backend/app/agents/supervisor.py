from backend.app.graph.state import AgentState
from backend.app.llm.provider_factory import LLMProviderFactory
from backend.app.llm.ollama_provider import generate_fallback_knowledge_response
from backend.app.tools.search_tools import clean_search_synthesis
from backend.app.utils.logger import logger

class SupervisorAgent:
    def __init__(self):
        pass

    def plan_and_route(self, state: AgentState) -> AgentState:
        query = state["input_query"].lower().strip()
        doc_id = state.get("document_id")
        provider = state.get("provider", "gemini")
        model = state.get("model", "gemini-1.5-flash")

        logger.info(f"Supervisor Agent analyzing query: '{state['input_query']}' (Selected document_id: '{doc_id}')")

        greetings = {"hi", "hii", "hiii", "hello", "hey", "heyy", "namaste", "hola", "good morning", "good evening", "good afternoon", "wassup", "what's up", "hy", "hyy"}

        plan = []
        is_rag_query = bool(doc_id) or any(w in query for w in ["rag", "document", "file", "index", "vector", "stored", "uploaded", "summary", "summarize", "summerize", "summarise", "summery", "pdf", "docx", "excel", "report"])

        if query in greetings or any(query.startswith(g) for g in ["hi ", "hii ", "hello ", "hey ", "namaste "]):
            plan = []
        elif is_rag_query:
            plan = ["rag_agent"]
        else:
            if any(w in query for w in ["research", "arxiv", "paper", "study", "wikipedia", "journal", "academic"]):
                plan.append("research_agent")
            if any(w in query for w in ["parse", "pdf", "excel", "ocr", "metadata", "extract"]):
                plan.append("document_agent")
            if any(w in query for w in ["code", "python", "java", "javascript", "sql", "bug", "html", "css", "refactor", "script", "function", "program"]):
                plan.append("code_agent")
            if any(w in query for w in ["csv", "data", "chart", "statistics", "trend", "dataframe", "table", "mean", "sum", "math", "calculate"]):
                plan.append("data_analysis_agent")
            if any(w in query for w in ["search", "web", "latest", "news", "duckduckgo", "github", "url", "what is", "who is", "explain", "prime minister", "president", "capital"]):
                plan.append("web_search_agent")
            if any(w in query for w in ["memory", "remember", "history", "previous"]):
                plan.append("memory_agent")

            if not plan:
                plan = ["web_search_agent"]

        state["execution_plan"] = plan
        state["current_agent"] = plan[0] if plan else "supervisor"
        logger.info(f"Supervisor Execution Plan created: {plan}")

        return state

    def synthesize_response(self, state: AgentState) -> AgentState:
        provider = state.get("provider", "gemini")
        model = state.get("model", "gemini-1.5-flash")
        user_settings = state.get("user_settings")
        llm = LLMProviderFactory.get_llm(provider=provider, model_name=model, user_settings=user_settings)

        query = state["input_query"]
        agent_outputs = state.get("agent_outputs", {})

        collected_info = []
        for agent_name, output in agent_outputs.items():
            if output and str(output).strip():
                collected_info.append(f"=== Insights from [{agent_name.upper()}] ===\n{output}\n")

        context = "\n\n".join(collected_info) if collected_info else "No sub-agent insights required."

        prompt = f"""You are the Lead Supervisor AI of OmniAgent AI, an advanced LangGraph Multi-Agent Ecosystem.

User Query: "{query}"

Sub-Agent Insights & Execution Data:
{context}

CRITICAL RESPONSE GUIDELINES:
1. Synthesize a comprehensive, detailed, beautifully structured response in clean Markdown.
2. Use clear section headings, key points, and bullet points to provide an in-depth answer.
3. Do NOT use any prefix like "Answer:" or "Response:". Start directly with the core information.
4. Do NOT output raw search URLs, titles, or '=== Tavily' headers.

Synthesize the final answer for the user:"""

        try:
            response = llm.invoke(prompt)
            final_text = response.content if hasattr(response, 'content') else str(response)
            import re
            if (
                final_text 
                and len(final_text.strip()) > 20 
                and "OmniAgent AI System processed your query" not in final_text
                and not final_text.startswith("[Gemini API Error")
                and not final_text.startswith("[Gemini Provider]")
                and "API key not valid" not in final_text
                and not final_text.startswith("=== Tavily")
            ):
                state["final_response"] = re.sub(r"^\*{0,2}(Direct\s+)?Answer:\*{0,2}\s*", "", final_text.strip(), flags=re.IGNORECASE)
            elif agent_outputs:
                output = list(agent_outputs.values())[-1]
                state["final_response"] = clean_search_synthesis(query, output)
            else:
                state["final_response"] = generate_fallback_knowledge_response(query, model)
        except Exception as e:
            logger.error(f"Supervisor synthesis fallback: {str(e)}")
            if agent_outputs:
                output = list(agent_outputs.values())[-1]
                state["final_response"] = clean_search_synthesis(query, output)
            else:
                state["final_response"] = generate_fallback_knowledge_response(query, model)

        import re
        if state.get("final_response"):
            state["final_response"] = re.sub(r"^\*{0,2}(Direct\s+)?Answer:\*{0,2}\s*", "", state["final_response"], flags=re.IGNORECASE).strip()

        return state

