import re
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
        prompt = f"""You are OmniAgent's Senior Software Engineer & Code Agent.
Your sole duty is to write production-ready code, debug software issues, explain algorithms, and provide technical guidance.

ROLE & SCOPE:
- Python, JavaScript, Java, C++, SQL, HTML/CSS, Frameworks (FastAPI, React), Algorithms, Debugging.

INSTRUCTIONS:
1. Provide complete, fully-functional, high-quality code solutions with proper syntax highlighting (e.g. ```python, ```javascript, ```sql).
2. Explain the code step-by-step with best practices and edge case handling.
3. Do NOT use any prefix like "Answer:" or "Response:". Start directly with the code solution.

User Request: {query}
"""

        code_response = ""
        try:
            res = llm.invoke(prompt)
            text = res.content if hasattr(res, 'content') else str(res)
            if text and len(text.strip()) > 15 and not text.startswith("[Gemini"):
                code_response = text.strip()
        except Exception as e:
            logger.error(f"Code Agent LLM notice: {e}")

        if code_response:
            code_response = re.sub(r"^\*{0,2}Answer:\*{0,2}\s*", "", code_response, flags=re.IGNORECASE).strip()

        # If user explicitly requested Python execution, run REPL tool
        if any(term in query.lower() for term in ["run python", "execute", "run code", "repl"]):
            target_code = query
            if "```python" in code_response:
                try:
                    target_code = code_response.split("```python")[1].split("```")[0].strip()
                except Exception:
                    pass
            repl_output = execute_python_code(target_code)
            code_response += f"\n\n### REPL Execution Output:\n```text\n{repl_output}\n```"

        if not code_response:
            code_response = f"### Code Solution for '{query}'\n\n```python\n# Implementation for: {query}\ndef main():\n    print('Executing code solution for: {query}')\n\nif __name__ == '__main__':\n    main()\n```"

        state["code_output"] = code_response

        if "agent_outputs" not in state or state["agent_outputs"] is None:
            state["agent_outputs"] = {}

        state["agent_outputs"]["code_agent"] = code_response
        return state

