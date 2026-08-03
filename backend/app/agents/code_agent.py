from backend.app.graph.state import AgentState
from backend.app.tools.python_repl import execute_python_code
from backend.app.llm.provider_factory import LLMProviderFactory
from backend.app.utils.logger import logger

class CodeAgent:
    def execute(self, state: AgentState) -> AgentState:
        query = state["input_query"]
        logger.info(f"Code Agent generating/debugging code for query: '{query}'")

        llm = LLMProviderFactory.get_llm(
            provider=state.get("provider"),
            model_name=state.get("model"),
            user_settings=state.get("user_settings")
        )
        prompt = f"""You are an Expert Senior Software Engineer and Code Agent.
Analyze the user's request, provide detailed code solutions (Python, Java, JS, HTML, CSS, SQL), debug explanations, and refactoring guidelines.

User Request: {query}
"""

        try:
            res = llm.invoke(prompt)
            code_response = res.content if hasattr(res, 'content') else str(res)
        except Exception as e:
            code_response = f"Code Agent analysis fallback for query: '{query}'"

        # If user explicitly requested Python execution, run REPL tool
        if "run python" in query.lower() or "execute" in query.lower():
            repl_output = execute_python_code(query)
            code_response += f"\n\n### REPL Execution Results:\n```text\n{repl_output}\n```"

        state["code_output"] = code_response

        if "agent_outputs" not in state or state["agent_outputs"] is None:
            state["agent_outputs"] = {}

        state["agent_outputs"]["code_agent"] = code_response
        return state
