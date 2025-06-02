from pydantic import BaseModel, Field
from typing import List
import re
import json

from agent import *
from parsers import *

class ProblemModel(BaseModel):
    quantity_name: List[str] = Field(
        ...,
        description="List of the quantity names involved in the problem. Calculated in (1.b), (2.b), and (4.b)"
    )
    equations: List[str] = Field(
        ...,
        description="List of mathematical equations relating the quantities. Calculated in (3.b), and (4.b)"
    )
    answer: str = Field(
        ...,
        description="The name of the quantity whose value must be found for solving the problem. Calculated in (2.b)"
    )

METHOD_TEMPLATE = """
You are an expert at solving math word problems. 
Given a math question, the goal is to follow the provided method to determine the variables and equations \
to solve the problem.

Provided method:
1. The goal is to identify the relevant quantities of the problem. We don't need to calculate them now.
1.a. Rewrite the statement, thinking step-by-step about which quantities are relevant.
1.b. Give a list [(description: str, quantity_name: str)] with the description of the quantity and the \
quantity name (a variable name using snake case). 

2. The goal is to identify the quantity that answers the problem. 
2.a. Rewrite the piece of the statement where something is required to be calculated as the answer. \
In general, it's in the final part of the statement.
2.b. The quantity that answers the problem was probably already part of the recognized ones in (1.b). \
If so, mention the quantity_name; if not, it's okay to create a quantity_name for it and a description. \
The description must specify that it's the final answer to the problem.

3. The goal is to identify the functional relationship as equations between the quantities.
3.a.  Rewrite the pieces of text that express a relationship between two or more quantities.
3.b. For each relationship, write a math equation between the respective variable names of the quantities \
defined in (1.b)
Remember to write "common knowledge" relationship between variables. For instance \
if measurement_in_cm and measurement_in_mm ara variables add measurement_in_cm * 10 = measurement_in_mm

4. The goal is to identify the constants in the statement and their relationship with the quantities.
4.a. Rewrite the pieces of text where any constant appears. Clue: this are the number literals that appear \
in the text: {number_literals}
4.b. For each constant, write mathematical equations between it and the quantities. Use the quantity names \
defined in (1.b).
For each variable identified remember to review if they are not a "common knowledge" constant. \
If they are, remember to add the respective equation. For instance day_of_week = 7 if day_of_week is a \
used variable.

5. The goal is to parse the last trace of messages and sum up everything in one JSON output that respects \
the following JSON schema:

Enclose the answer using Markdown code block formatting (```json <generated JSON> ```):

```json
{json}
```

<math_problem>
{question}
</math_problem>

"""

def extract_numbers(s):
    # Use regular expression to find all numbers (integers and decimals)
    numbers = re.findall(r'\d+(?:\.\d+)?', s)
    return numbers

def make_prompt_method(question):
    number_literals = extract_numbers(question)
    return METHOD_TEMPLATE.format(question=question, 
                                  number_literals=number_literals, 
                                  json=json.dumps(ProblemModel.model_json_schema(),indent=2))


class EquationChecker(Parser):
    def forward(self, math_model):
        result = ParserValue(value = math_model)
        
        known_non_variables = {"sqrt", "log", "sin", "cos", "tan", "exp", "abs", "min", "max", "pow"}
        
        def extract_potential_variables(equation):
            tokens = re.findall(r"[a-zA-Z_]\w*", equation)
            return [token for token in tokens if token not in known_non_variables]
        
        used_variables_set = set()
        for eq in math_model.equations:
            used_variables_set.update(extract_potential_variables(eq))
        
        declared_variables_set = set(math_model.quantity_name)
        
        undefined_variables = used_variables_set - declared_variables_set
        if undefined_variables:
            result.warn(f"Some variables used in \"equations\" field are not declared in \"quantity_name\" field: {undefined_variables}. All variables must be used")

        unused_variables = declared_variables_set - used_variables_set
        if unused_variables:
            result.warn(f"Some variables declared in \"quantity_name\" field are not used in \"equations\" field: {unused_variables}. All variables must be used")

        if math_model.answer not in used_variables_set:
            return ParserValue(error = f"Answer variable (\"answer\" field) is not used in any equation (\"equations\" field): {math_model.answer}")

        if math_model.answer not in declared_variables_set:
            result.warn(f"Answer variable {math_model.answer} was not included in \"quantity_name\" field.")
            
        n_eqs = len(math_model.equations)
        n_vars = len(math_model.quantity_name)
        if n_eqs < n_vars:
            result.warn(f"{n_vars} variables are declared, but only {n_eqs} were extracted. A problem must have more equations than variables to have a single solution.")
        
        return result

async def create_method_agent(question, fn_llm):
    json_parser = JSONParser()
    pydantic_parser = PydanticParser(ProblemModel)
    equation_checker_parser = EquationChecker()
    
    def parse_math_method(x):
        x = json_parser(x)
        x = pydantic_parser(x)
        x = equation_checker_parser(x)
        return x
    
    agent = Agent(fn_llm)
    method_prompt = make_prompt_method(question)
    await agent.send_user_message(method_prompt)
    result = await agent.retry_until_parse(parse_math_method)

    return result

from math_solver import *

async def solve_method_agent(system, fn_llm):
    agent = Agent(fn_llm)
    coder_prompt = make_prompt_code(system)
    await agent.send_user_message(coder_prompt)
    result = await agent.retry_until_parse(CodeParser())
    return result

async def solve_question(question):
    fn_llm = partial(chat, model=BIG_MODEL, verbose=False)
    system = await create_method_agent(question, fn_llm)
    solution = await solve_method_agent(system, fn_llm)
    return {'predicted': solution, "response": True}