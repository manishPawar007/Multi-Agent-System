import sys
import io
import traceback

def execute_python_code(code: str) -> str:
    """Executes Python code in a sandboxed REPL environment and captures stdout/stderr."""
    old_stdout = sys.stdout
    old_stderr = sys.stderr
    redirected_output = io.StringIO()
    redirected_error = io.StringIO()

    sys.stdout = redirected_output
    sys.stderr = redirected_error

    exec_globals = {
        "__builtins__": __builtins__,
        "sys": sys,
        "io": io
    }

    try:
        clean_code = code.strip()
        if clean_code.startswith("```python"):
            clean_code = clean_code[9:]
        if clean_code.startswith("```"):
            clean_code = clean_code[3:]
        if clean_code.endswith("```"):
            clean_code = clean_code[:-3]

        exec(clean_code.strip(), exec_globals)

        out = redirected_output.getvalue()
        err = redirected_error.getvalue()

        output = ""
        if out:
            output += f"Output:\n{out}\n"
        if err:
            output += f"Errors:\n{err}\n"
        if not output:
            output = "Code executed successfully with no stdout output."

        return output
    except Exception as e:
        return f"Python Execution Exception: {str(e)}\n{traceback.format_exc()}"
    finally:
        sys.stdout = old_stdout
        sys.stderr = old_stderr
