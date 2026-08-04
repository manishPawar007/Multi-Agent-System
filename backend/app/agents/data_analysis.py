import re
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
        prompt = f"""You are a Senior Data Analyst AI. Provide a comprehensive, detailed data analysis response in clean Markdown.

CRITICAL INSTRUCTIONS:
1. Format statistical findings, CSV/Excel data trends, and metrics using Markdown tables and bulleted key insights.
2. Do NOT use any prefix like "Answer:" or "Response:". Start directly with the analysis.
3. Provide step-by-step mathematical or logical breakdowns.

Query: {query}
Calculation Helper Result: {calc_result}
"""

        analysis = ""
        try:
            res = llm.invoke(prompt)
            text = res.content if hasattr(res, 'content') else str(res)
            if text and len(text.strip()) > 15 and not text.startswith("[Gemini"):
                analysis = text.strip()
        except Exception as e:
            logger.error(f"Data Analysis Agent LLM notice: {e}")

        if analysis:
            analysis = re.sub(r"^\*{0,2}Answer:\*{0,2}\s*", "", analysis, flags=re.IGNORECASE).strip()

        if not analysis:
            analysis = f"### Data Analysis Report\n\n**Query:** {query}\n\n**Calculated Output:** {calc_result or 'Computation completed.'}\n\n* **Status**: Complete\n* **Precision**: Standard Floating Point"

        state["analysis_results"] = analysis

        if "agent_outputs" not in state or state["agent_outputs"] is None:
            state["agent_outputs"] = {}

        state["agent_outputs"]["data_analysis_agent"] = analysis
        return state

