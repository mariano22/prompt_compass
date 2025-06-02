import json

from parsers import *

TEMPLATE_SOLVER = """
You are a Python expert with experience in numerical optimization.
Given a JSON describing a system of equations, you must write Python code that builds and solves the system using SciPy.
The system of equations in JSON format contains three keys:
- "quantity_name": a list of str with the system's variables.
- "equations": a list of str with the equations of the system.
- "answer": the system variable that must be calculated to solve the problem.
Equations are not necessarily linear.

You must produce Python code. You can reason before coding.
1. Use this interface to solve the system:
```python
from scipy.optimize import root
sol = root(system_fn, initial_guess, method='hybr')
```

2. Inside system_fn(vars):
  2.a. Interpret vars as a list of floats.
  2.b. Unpack the variables in the same order as given in "quantity_name".
2.c. Return a list of residuals (i.e., lhs - rhs) for each equation, in any order, but of the same length as vars.

3. Your initial guess should be [1.0] * len(quantity_name).

4. At the end, you can create a dictionary mapping variable names to calculated values.\
You can do this by doing zip(quantity_name, sol.x).

5. The answer is the value of the variable specified in the "answer" key of the system, rounded to the nearest integer.
Return the answer. Do not print anything. Do not write a main section.

<example_of_input>
{example_system}
</example_of_input>

<example_of_output>
{example_python_code}
</example_of_output>

<input_system>
{system}
</input_system>

Remember to enclose the code using Markdown code block formatting (```python <your-code-here> ```).
"""

EXAMPLE_SYSTEM = {
  "quantity_name": [
    "cost_shoes",
    "monthly_allowance",
    "months_saving",
    "charge_per_lawn",
    "charge_per_driveway",
    "lawns_mowed",
    "driveways_shoveled",
    "money_left",
    "total_money"
  ],
  "equations": [
    "total_money = (monthly_allowance * months_saving) + (charge_per_lawn * lawns_mowed) + (charge_per_driveway * driveways_shoveled)",
    "total_money = cost_shoes + money_left",
    "cost_shoes = 95",
    "monthly_allowance = 5",
    "months_saving = 3",
    "charge_per_lawn = 15",
    "charge_per_driveway = 7",
    "money_left = 15",
    "lawns_mowed = 4"
  ],
  "answer": "driveways_shoveled"
}

EXAMPLE_PYTHON_CODE = """
```python
from scipy.optimize import root

# Define the system function
def system_fn(vars):
    (
        cost_shoes,
        monthly_allowance,
        months_saving,
        charge_per_lawn,
        charge_per_driveway,
        lawns_mowed,
        driveways_shoveled,
        money_left,
        total_money
    ) = vars

    return [
        total_money - (
            (monthly_allowance * months_saving) +
            (charge_per_lawn * lawns_mowed) +
            (charge_per_driveway * driveways_shoveled)
        ),
        total_money - (cost_shoes + money_left),
        cost_shoes - 95,
        monthly_allowance - 5,
        months_saving - 3,
        charge_per_lawn - 15,
        charge_per_driveway - 7,
        money_left - 15,
        lawns_mowed - 4
    ]

def solve():
    # Initial guess: one per variable
    initial_guess = [1.0] * 9
    
    # Solve the system
    sol = root(system_fn, initial_guess, method='hybr')
    
    # Variables list
    quantity_name = [
        "cost_shoes",
        "monthly_allowance",
        "months_saving",
        "charge_per_lawn",
        "charge_per_driveway",
        "lawns_mowed",
        "driveways_shoveled",
        "money_left",
        "total_money"
    ]
    
    # Build result dictionary
    solution = {name: val for name, val in zip(quantity_name, sol.x)}
    
    return round(solution["driveways_shoveled"])
```
"""

def make_prompt_code(system):
    return TEMPLATE_SOLVER.format(
        example_system = json.dumps(EXAMPLE_SYSTEM, indent=2),
        example_python_code = EXAMPLE_PYTHON_CODE,
        system = system.model_dump_json(indent=2)
    )
    
def parse_completion_method(raw):
    raw_code = parse_markers(raw, start_marker = "```python", end_marker = "```")
    exec(raw_code)
    return solve()

class CodeParser(Parser):
    def forward(self, raw_str):
        if "```python" not in raw_str:
            return ParserValue(error = "No python code delimiter found: \"```python\"")
        code_str = parse_markers(raw_str, start_marker = "```python", end_marker = "```")
        
        namespace = {}
        try:
            exec(code_str, namespace)
        except Exception as e:
            error_msg = f"Error loading the produced python code:"
            error_msg += "\n" + prompt_create_tag("exception_loading_code", str(e))
            return ParserValue(error = error_msg)

        try:
            answer = eval("solve()", namespace)
        except Exception as e:
            error_msg = f"Error executing solve() in the produced python code"
            error_msg += "\n" + prompt_create_tag("exception_executing_code", str(e))
            return ParserValue(error = error_msg)

        return ParserValue(value = answer)