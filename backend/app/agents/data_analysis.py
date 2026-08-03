from backend.app.graph.state import AgentState
from backend.app.tools.calculator import calculate_expression
from backend.app.llm.provider_factory import LLMProviderFactory
from backend.app.utils.logger import logger

class DataAnalysisAgent:
    def execute(self, state: AgentState) -> AgentState:
        query = state["input_query"]
        logger.info(f"Data Analysis Agent analyzing request: '{query}'")

        # Evaluate math calculations if detected
        calc_result = ""
        if any(c in query for c in ["+", "-", "*", "/", "^"]):
            calc_result = calculate_expression(query)

        llm = LLMProviderFactory.get_llm(
            provider=state.get("provider"),
            model_name=state.get("model"),
            user_settings=state.get("user_settings")
        )
        prompt = f"""You are a Senior Data Analyst AI. Analyze statistics, CSV/Excel data trends, tabular formatting, and report summaries.

Query: {query}
Calculation Helper Result: {calc_result}
"""

        try:
            res = llm.invoke(prompt)
            analysis = res.content if hasattr(res, 'content') else str(res)
        except Exception:
            analysis = f"Data Analysis result for: {query}\n{calc_result}"

        state["analysis_results"] = analysis

        if "agent_outputs" not in state or state["agent_outputs"] is None:
            state["agent_outputs"] = {}

        state["agent_outputs"]["data_analysis_agent"] = analysis
        return state
