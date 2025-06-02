prompt_template_example_failing = """
<failed_example example>
    <question>
        {question}
    </question>

<expected_answer>
{{
    "thoughts": {thoughts},
    "answer": {answer}
}}
</expected_answer>

<wrong_prediction>
{{
    "predicted_thoughts": {predicted_thoughts},
    "predicted": {predicted}
}}
</wrong_prediction>
</failed_example>
"""

prompt_corrector = """
You are an agent responsible for improving the quality of instructions provided to an LLM agent. The goal of the LLM agent is to solve a math problem.
Your task is to improve the instructions provided to the LLM agent to increase accuracy on a test set. 
You will be provided the current prompt sent to the LLM agent and cases wrongly solved by the agent.
Please rewrite the prompt that will be sent to the LLM agent. 
Consider adding MORE steps that consider the root causes of the observed mistakes.
Consider also adding examples of the behaviour that causes the errors.

Return the result in JSON format as follows:
{{
  "reasoning": "...",  # A reasoning about the pitfalls you observe
  "mitigation": "...", # The mitigation strategy you propose
  "new_prompt": ...    # The new proposed prompt
}}

<examples_failing>
{examples_failing}
</examples_failing>

<current_prompt>
{current_prompt}
</current_prompt>

"""

def make_wrong_examples_prompt(base_prompt, wrong_examples):
    examples_str = '\n'.join([prompt_template_example_failing.format(
            question=e['question'],
            thoughts=e['thoughts'],
            answer=e['answer'],
            predicted_thoughts=e['predicted_thoughts'],
            predicted=e['predicted'],
        ) for e in wrong_examples])
    
    return prompt_corrector.format(current_prompt=base_prompt, examples_failing = examples_str)

class MetaPromptSolution(BaseModel):
    """A new and improved prompt for the LLM math agent with step-by-step analysis and reasoning and final answer"""
    reasoning: str = Field(..., description="A reasoning about the pitfalls you observe in the examples failing")
    mitigation: str = Field(..., description="The mitigation strategies you propose to improve the prompt and solve the failing cases")
    new_prompt: str = Field(..., description="The new prompt proposed to be used")

def improve_prompt(results_examples):
    wrong_cases = [r for r in results_examples['results'] if not r['api_error'] and not r['format_error'] and not r['pass']]
    improving_prompt = make_wrong_examples_prompt(prompt_template_cot, wrong_cases[:12])
    return instructor_client.chat.completions.create(
            model="o3",
            messages=messages,
            response_model=MetaPromptSolution
        )

def pprint(meta_prompt_result):
    print(meta_prompt_result.reasoning)
    print('==========')
    print(meta_prompt_result.mitigation)
    print('==========')
    print(meta_prompt_result.new_prompt)