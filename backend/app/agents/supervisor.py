import re

from backend.app.graph.state import AgentState
from backend.app.llm.provider_factory import LLMProviderFactory
from backend.app.llm.ollama_provider import generate_fallback_knowledge_response
from backend.app.tools.search_tools import clean_search_synthesis
from backend.app.utils.logger import logger, extract_llm_text

class SupervisorAgent:
    def __init__(self):
        pass

    def plan_and_route(self, state: AgentState) -> AgentState:
        query = state["input_query"].lower().strip()
        doc_id = state.get("document_id")

        logger.info(f"Supervisor Agent analyzing query: '{state['input_query']}' (Selected document_id: '{doc_id}')")

        greetings = {"hi", "hii", "hiii", "hello", "hey", "heyy", "namaste", "hola", "good morning", "good evening", "good afternoon", "wassup", "what's up", "hy", "hyy"}

        plan = []

        if query in greetings or any(query == g for g in greetings) or (len(query) < 6 and any(query.startswith(g) for g in ["hi", "hey", "hello"])):
            state["execution_plan"] = []
            state["current_agent"] = "supervisor"
            return state

        # Sub-agent detection conditions
        is_rag_query = bool(doc_id) or any(w in query for w in ["uploaded pdf", "my pdf", "uploaded file", "target document", "this pdf", "in the pdf", "uploaded document", "chromadb", "document"])
        is_code = any(w in query for w in ["code", "python", "java", "javascript", "js", "sql", "bug", "html", "css", "refactor", "script", "function", "program", "algorithm", "compiler", "api endpoint", "write a function", "write code", "create a script"])
        is_math_data = any(w in query for w in ["csv", "excel", "chart", "statistics", "trend", "dataframe", "table", "math", "calculate", "percentage", "data analysis", "data analytics"])
        is_research = any(w in query for w in ["arxiv", "paper", "scientific study", "journal", "academic literature", "methodology", "literature review"])
        is_doc = any(w in query for w in ["ocr", "parse pdf", "extract text from image", "metadata extraction", "document format"])
        is_memory = any(w in query for w in ["remember", "history", "previous chat", "what did i ask", "earlier", "recap"])
        is_search = any(w in query for w in ["search", "web", "latest", "news", "who is", "where is", "when did", "prime minister", "president", "capital", "weather", "live score", "current price", "update", "today"])

        # Multi-Agent Routing: Add all relevant sub-agents to execution plan
        if is_rag_query:
            plan.append("rag_agent")
        if is_doc and "document_agent" not in plan:
            plan.append("document_agent")
        if is_research and "research_agent" not in plan:
            plan.append("research_agent")
        if is_search and "web_search_agent" not in plan:
            plan.append("web_search_agent")
        if is_code and "code_agent" not in plan:
            plan.append("code_agent")
        if is_math_data and "data_analysis_agent" not in plan:
            plan.append("data_analysis_agent")
        if is_memory and "memory_agent" not in plan:
            plan.append("memory_agent")

        # If general query with no sub-agent keywords, auto-assign Web Search or Research agent for factual grounding
        if not plan:
            if any(w in query for w in ["explain", "how does", "what is", "why is", "compare", "difference", "tutorial", "guide", "overview"]):
                plan.append("web_search_agent")
            else:
                plan.append("web_search_agent")

        state["execution_plan"] = plan
        state["current_agent"] = plan[0] if plan else "supervisor"
        logger.info(f"Supervisor Multi-Agent Execution Plan created: {plan}")

        return state

    def _clean_agent_output_text(self, text: str) -> str:
        if not text:
            return ""
        cleaned = str(text).strip()
        cleaned = re.sub(r"^\*{0,2}(Direct\s+)?(Answer|Response):\*{0,2}\s*", "", cleaned, flags=re.IGNORECASE)
        cleaned = re.sub(r"(?m)^===.*$", "", cleaned).strip()
        cleaned = re.sub(r"(?im)^(Title|URL|Snippet|Relevance|Search Results|Tavily AI Search Results|Live Web Search Results|Wikipedia Search Results|Arxiv Academic Search Results):.*$", "", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        return cleaned.strip()

    def _is_raw_noise(self, text: str) -> bool:
        if not text:
            return True
        return bool(re.search(r"===|Title:|URL:|Snippet:|Relevance:|Tavily AI|DuckDuckGo|Wikipedia Search|Arxiv Academic", text, re.IGNORECASE))

    def _get_best_agent_output(self, agent_outputs: dict) -> str:
        if not agent_outputs:
            return ""
        if "web_search_agent" in agent_outputs and agent_outputs["web_search_agent"]:
            return agent_outputs["web_search_agent"]
        if "rag_agent" in agent_outputs and agent_outputs["rag_agent"]:
            return agent_outputs["rag_agent"]
        return next((o for o in agent_outputs.values() if o and str(o).strip()), "")

    def synthesize_response(self, state: AgentState) -> AgentState:
        provider = state.get("provider", "gemini")
        model = state.get("model", "gemini-2.0-flash")
        user_settings = state.get("user_settings")
        llm = LLMProviderFactory.get_llm(provider=provider, model_name=model, user_settings=user_settings)

        query = state["input_query"]
        agent_outputs = state.get("agent_outputs", {})

        # Prioritize single specialized agent output if it's the only one executed
        if len(agent_outputs) == 1 and "code_agent" in agent_outputs and agent_outputs["code_agent"]:
            state["final_response"] = self._clean_agent_output_text(agent_outputs["code_agent"])
            return state

        collected_info = []
        for agent_name, output in agent_outputs.items():
            cleaned_output = self._clean_agent_output_text(output)
            if cleaned_output:
                collected_info.append(f"=== Insights from [{agent_name.upper()}] ===\n{cleaned_output}\n")

        context = "\n\n".join(collected_info) if collected_info else "No sub-agent insights required."

        prompt = f"""You are the Lead Supervisor AI of OmniAgent AI, orchestrating a team of specialized AI agents.

User Query: "{query}"

Sub-Agent Insights & Execution Data:
{context}

CRITICAL RESPONSE GUIDELINES:
1. Provide a detailed, comprehensive, and well-structured answer to the user query.
2. ALWAYS use Markdown formatting with clear section headings (### Overview, ### Key Stages / Core Components, ### Key Takeaways), bullet points, and bold text.
3. For explanatory, process, or lifecycle questions (e.g. "explain ML lifecycle", "what is deep learning", "explain RAG architecture"):
   - Provide a deep, step-by-step or phase-by-phase breakdown.
   - Explain each phase/concept in detail with clear bullet points.
   - Never return a brief 1-2 sentence answer for complex concepts or explanation requests.
4. Do NOT use any prefix like "Answer:" or "Response:."
5. Do NOT output raw search URLs, raw titles, or source dump markers such as "=== Tavily".
6. If you have sub-agent findings, integrate them naturally and cite the evidence or reasoning.

Synthesize the final answer for the user:"""

        try:
            response = llm.invoke(prompt)
            final_text = extract_llm_text(response)
            final_text = self._clean_agent_output_text(final_text)
            if final_text and len(final_text.strip()) > 20 and "OmniAgent AI System processed your query" not in final_text:
                if self._is_raw_noise(final_text) and agent_outputs:
                    fallback_output = self._get_best_agent_output(agent_outputs)
                    state["final_response"] = clean_search_synthesis(query, fallback_output)
                else:
                    state["final_response"] = final_text
            elif agent_outputs:
                fallback_output = self._get_best_agent_output(agent_outputs)
                state["final_response"] = clean_search_synthesis(query, fallback_output)
            else:
                state["final_response"] = generate_fallback_knowledge_response(query, model)
        except Exception as e:
            logger.error(f"Supervisor synthesis fallback: {str(e)}")
            fallback_output = self._get_best_agent_output(agent_outputs)
            if fallback_output:
                state["final_response"] = clean_search_synthesis(query, fallback_output)
            else:
                state["final_response"] = generate_fallback_knowledge_response(query, model)

        if state.get("final_response"):
            state["final_response"] = self._clean_agent_output_text(state["final_response"])

        return state


