
prompt_template_naive = """
You are an expert at solving math word problems. Given a question, provide a solution as a numerical value only. 
Return the numerical value only.

<question>
{question}
</question>

Return the numerical value only. No characters, no reasoning. Only an integer.
"""

def make_naive_prompt(question):
    return prompt_template_naive.format(question=question)

prompt_template_cot = """You are an expert at solving math word problems. 
Think step by step to find the answer.

Return the result in JSON format as follows:
{{
  "thoughts": "...",
  "value_first_attempt": "...",
  "reflect": "...",
  "value": "...",
}}
"value" field contain an evaluable python expression without variables (only numbers and operations) or just numerical constant.

<question>
{question}
</question>"""

def make_cot_prompt(question):
    return prompt_template_cot.format(question=question)

prompt_template_example = """
<example>
    <question>
        {question}
    </question>
<answer>
{{
    "thoughts": {thoughts},
    "value": {value}
}}
</answer>
</example>
"""

prompt_template_cot_examples = """You are an expert at solving math word problems. 
Think step by step to find the answer.

Return the result in JSON format as follows:
{{
  "thoughts": "...",
  "value": ...
}}

<examples>
{examples}
</examples>

<question>
{question}
</question>"""

def make_cot_fixed_examples_prompt(question, examples):
    return make_cot_examples_prompt(question, examples, 'thoughts')

def make_cot_learned_examples_prompt(question, examples):
    return make_cot_examples_prompt(question, examples, 'predicted_thoughts')

def make_cot_examples_prompt(question, examples, example_field):
    examples_str = '\n'.join([
        prompt_template_example.format(
            question=e['question'],
            thoughts=e[example_field],
            value=e['answer'],
        ) for e in examples])
    return prompt_template_cot_examples.format(question=question, examples = examples_str)