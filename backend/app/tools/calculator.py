import math
import re

def calculate_expression(expression: str) -> str:
    """Evaluates mathematical expressions safely."""
    try:
        sanitized = re.sub(r'[^0-9\+\-\*\/\(\)\.\^\s\%\,]', '', expression)
        sanitized = sanitized.replace('^', '**')

        allowed_names = {
            "sin": math.sin, "cos": math.cos, "tan": math.tan,
            "sqrt": math.sqrt, "log": math.log, "exp": math.exp,
            "pi": math.pi, "e": math.e, "pow": math.pow, "abs": abs
        }

        result = eval(sanitized, {"__builtins__": None}, allowed_names)
        return f"Result: {result}"
    except Exception as e:
        return f"Math Calculation Error: {str(e)}"
