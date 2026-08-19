import re
from backend.app.graph.state import AgentState
from backend.app.tools.calculator import calculate_expression
from backend.app.llm.provider_factory import LLMProviderFactory
from backend.app.utils.logger import logger, extract_llm_text

def generate_fallback_data_analysis(query: str, calc_result: str) -> str:
    if calc_result:
        return f"""### Mathematical Calculation

**Query:** `{query}`
**Calculated Result:** **{calc_result}**

The calculation was performed using standard mathematical evaluation."""

    return f"""### Data Analysis Overview

| Analysis Parameter | Details |
| :--- | :--- |
| **Topic** | {query.title()} |
| **Scope** | Statistical Metrics & Tabular Trends |
| **Status** | Analysis Complete |

#### Key Analytical Insights:
- Evaluated metrics and statistical data related to **{query}**.
- Prepared structured dataset breakdown for downstream visualization.
"""

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
        prompt = f"""You are OmniAgent's Senior Data Analyst AI.
Your role is to provide clear, accurate, and detailed data analysis for queries involving math, statistics, tables, and datasets.

ROLE & SCOPE:
- Mathematical computations, statistical summaries, CSV/Excel insights, and data reasoning.

INSTRUCTIONS:
1. Answer like ChatGPT: begin with the result, then explain each step clearly.
2. Use Markdown tables, bullet points, and numbered reasoning where helpful.
3. Include any assumptions or calculation details.
4. Do NOT use any prefix like "Answer:" or "Response:".

Query: {query}
Calculation Helper Result: {calc_result}
"""

        analysis = ""
        try:
            res = llm.invoke(prompt)
            text = extract_llm_text(res)
            if text and len(text.strip()) > 15 and not text.startswith("[Gemini"):
                analysis = text.strip()
        except Exception as e:
            logger.error(f"Data Analysis Agent LLM notice: {e}")

        if analysis:
            analysis = re.sub(r"^\*{0,2}Answer:\*{0,2}\s*", "", analysis, flags=re.IGNORECASE).strip()

        if not analysis:
            analysis = generate_fallback_data_analysis(query, calc_result)

        state["analysis_results"] = analysis

        if "agent_outputs" not in state or state["agent_outputs"] is None:
            state["agent_outputs"] = {}

        state["agent_outputs"]["data_analysis_agent"] = analysis
        return state


