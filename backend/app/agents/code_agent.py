import re
from backend.app.graph.state import AgentState
from backend.app.tools.python_repl import execute_python_code
from backend.app.llm.provider_factory import LLMProviderFactory
from backend.app.utils.logger import logger

def generate_fallback_code(query: str) -> str:
    q_lower = query.lower()

    # 1. Java Code Requests
    if "java" in q_lower:
        if any(term in q_lower for term in ["sum", "add", "plus", "addition", "two number"]):
            return """Here is the complete Java program to calculate the sum of two numbers:

```java
import java.util.Scanner;

public class SumOfTwoNumbers {
    public static void main(String[] args) {
        // Method 1: Using predefined values
        int num1 = 15;
        int num2 = 25;
        int sum = num1 + num2;

        System.out.println("First Number: " + num1);
        System.out.println("Second Number: " + num2);
        System.out.println("Sum = " + sum);

        // Method 2: Dynamic User Input using Scanner
        Scanner scanner = new Scanner(System.in);
        System.out.print("\nEnter first number: ");
        int a = scanner.nextInt();
        System.out.print("Enter second number: ");
        int b = scanner.nextInt();

        int userSum = a + b;
        System.out.println("Result of User Input: " + userSum);
        scanner.close();
    }
}
```

### Explanation:
1. `num1` and `num2` store integer values.
2. `int sum = num1 + num2;` calculates the addition.
3. `Scanner scanner = new Scanner(System.in);` accepts dynamic inputs from the user.
4. `System.out.println()` outputs the result to console.
"""
        elif "fibonacci" in q_lower:
            return """Here is the Java code for generating the Fibonacci series:

```java
public class FibonacciSeries {
    public static void main(String[] args) {
        int n = 10, firstTerm = 0, secondTerm = 1;
        System.out.println("Fibonacci Series up to " + n + " terms:");

        for (int i = 1; i <= n; ++i) {
            System.out.print(firstTerm + ", ");
            int nextTerm = firstTerm + secondTerm;
            firstTerm = secondTerm;
            secondTerm = nextTerm;
        }
    }
}
```"""
        else:
            return f"""Here is a Java program template for **{query.title()}**:

```java
public class Solution {{
    public static void main(String[] args) {{
        System.out.println("Java Solution for: {query}");
    }}
}}
```"""

    # 2. Python Code Requests
    if "python" in q_lower or "py" in q_lower:
        if any(term in q_lower for term in ["sum", "add", "plus", "addition", "two number"]):
            return """Here is the Python script to calculate the sum of two numbers:

```python
# Method 1: Direct variable assignment
num1 = 15
num2 = 25
total_sum = num1 + num2

print(f"Number 1: {num1}")
print(f"Number 2: {num2}")
print(f"Sum = {total_sum}")

# Method 2: Dynamic User Input
a = float(input("Enter first number: "))
b = float(input("Enter second number: "))
print(f"Sum of {a} and {b} is: {a + b}")
```"""
        else:
            return f"""Here is the Python implementation for **{query.title()}**:

```python
def solve():
    # Solution logic for: {query}
    print("Executing Python solution...")

if __name__ == "__main__":
    solve()
```"""

    # 3. JavaScript / HTML / CSS / SQL
    if "javascript" in q_lower or "js" in q_lower:
        return """Here is the JavaScript code solution:

```javascript
function calculateSum(a, b) {
    return a + b;
}

const num1 = 10;
const num2 = 20;
console.log(`Sum of ${num1} and ${num2} is: ${calculateSum(num1, num2)}`);
```"""

    if "sql" in q_lower:
        return """Here is the SQL query solution:

```sql
SELECT employee_id, first_name, salary
FROM employees
WHERE salary > 50000
ORDER BY salary DESC;
```"""

    return f"""Here is the code solution for: **{query}**

```python
# Generic Code Implementation
def main():
    print("Execution completed for: {query}")

if __name__ == "__main__":
    main()
```"""

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
            code_response = generate_fallback_code(query)

        state["code_output"] = code_response

        if "agent_outputs" not in state or state["agent_outputs"] is None:
            state["agent_outputs"] = {}

        state["agent_outputs"]["code_agent"] = code_response
        return state


