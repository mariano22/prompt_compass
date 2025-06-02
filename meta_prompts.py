prompt_template_cot = """
You are an expert at solving math word problems. For each question, follow these steps:
1. Carefully read and analyze the problem. Identify all relevant quantities, relationships, and units.
2. Define any variables needed and write out equations or expressions that represent the relationships in the problem.
3. Show all intermediate calculations step by step, including unit conversions if necessary.
4. Clearly state your reasoning at each step, explaining how you arrive at each calculation.
5. After completing the calculations, check that your answer makes sense in the context of the problem.
6. At the end, clearly state the final numerical answer.

Format your response as follows:
{{
  "thoughts": "<step-by-step reasoning and calculations>",
  "value": <final numerical answer>
}}

<question>
{question}
</question>
"""

prompt_template_cot = """
You are an expert at solving math word problems. For each question, follow these steps:

1. Carefully read and analyze the problem. Paraphrase the problem in your own words, clarifying all relationships, quantities, and units. Identify what is being asked.
2. Identify and explicitly state any potentially ambiguous or tricky language (e.g., 'twice more', '50% taller', 'every other day', 'groups of 3', etc.). Explain how you interpret these phrases and why.
3. Define all variables needed and write out equations or expressions that represent the relationships in the problem. Clearly state what each variable represents.
4. Show all intermediate calculations step by step, including all unit conversions. Clearly state the reasoning behind each calculation.
5. At each step, check for common pitfalls, such as:
   - Confusing 'twice as many' with 'twice more than'
   - Confusing percent increase with percent of total
   - Confusing combinations (C(n, r)) with partitioning into groups
   - Not accounting for elapsed time or sequence of events
   - Off-by-one errors in counting sequences or intervals
6. After completing the calculations, check that your answer makes sense in the context of the problem. Re-read the problem and verify that all conditions are satisfied.
7. At the end, clearly state the final numerical answer.
8. If there are multiple plausible interpretations, briefly mention them and explain why you chose your approach.

Common mistakes to avoid (with examples):
- Misreading 'twice more' as 'twice as many' (e.g., 'twice more than 800' means 800 + 2*800 = 2400, not 2*800 = 1600)
- Treating '50% taller' as '50% of' instead of '150% of original'
- Using combinations when the problem asks for partitioning (e.g., dividing 21 students into groups of 3 is 21/3 = 7, not C(21,3))
- Not converting units (e.g., pounds to ounces)
- Not accounting for all time intervals or steps in a sequence

Format your response as follows:
{{
  "thoughts": "<step-by-step reasoning and calculations>",
  "value": <final numerical answer>
}}

<question>
{question}
</question>
"""

prompt_template_cot = """
You are an expert at solving math word problems. For each question, follow these steps in detail:

1. Carefully read and paraphrase the problem in your own words, clarifying all relationships, quantities, and units. Explicitly state what is being asked.
2. Identify and explicitly state any potentially ambiguous or tricky language (e.g., 'twice more', '50% taller', 'every other day', 'groups of 3', etc.). For each, explain all plausible interpretations and state which you will use and why.
3. Define all variables needed, and write out all equations or expressions that represent the relationships in the problem. Clearly state what each variable represents.
4. Show all intermediate calculations step by step, including all unit conversions. At each step, explicitly state the units and reasoning behind the calculation.
5. At each step, check for common pitfalls, such as:
   - Misinterpreting comparative language (e.g., 'twice more than 800' means 800 + 2*800 = 2400, not 2*800 = 1600)
   - Confusing percent increase with percent of total (e.g., '50% taller' means 150% of original)
   - Using combinations when the problem asks for partitioning (e.g., dividing 21 students into groups of 3 is 21/3 = 7, not C(21,3))
   - Not converting units (e.g., cents to dollars, pounds to ounces)
   - Not accounting for all time intervals or steps in a sequence (e.g., 'every other day for 2 weeks' means 7 gigs, not 14)
   - Off-by-one errors in counting sequences or intervals
6. After completing the calculations, plug your final answer back into the original problem to verify that it satisfies all conditions and makes sense in context. If it does not, re-examine your steps.
7. Clearly state the final numerical answer, with units.
8. If there are multiple plausible interpretations, briefly mention them and explain why you chose your approach. If the answer would be different under another interpretation, state what it would be.

Common mistakes to avoid (with examples):
- Misreading 'twice more' as 'twice as many' (e.g., 'twice more than 800' means 800 + 2*800 = 2400, not 2*800 = 1600)
- Treating '50% taller' as '50% of' instead of '150% of original'
- Using combinations when the problem asks for partitioning (e.g., dividing 21 students into groups of 3 is 21/3 = 7, not C(21,3))
- Not converting units (e.g., pounds to ounces, cents to dollars)
- Not accounting for all time intervals or steps in a sequence
- Not checking that the answer fits all conditions in the problem

Format your response as follows:
{{
  "thoughts": "<step-by-step reasoning and calculations, with explicit equations, units, and checks>",
  "value": <final numerical answer with units>
}}

<question>
{question}
</question>
"""

prompt_template_cot_o3 = """
• Introduce a mandatory multi‑step framework:  (A) Re‑state & label data  (B) Plan  (C) Execute line‑by‑line arithmetic  (D) Sanity‑check  (E) Produce answer.
• Make the JSON schema strict: "thoughts" must show the full working, "answer" a bare number.
• Warn that describing operations in words without the accompanying arithmetic is incorrect and will be graded as failure.
• Give two miniature examples: one correct (with explicit numbers) and one incorrect (only narrative) so the agent sees the difference.
• Remind the agent to watch for off‑by‑one, fraction, unit‑conversion and conditional‑logic traps.
• Encourage plugging the result back into the original context as a quick validation step.
These measures force the agent to surface each inference, dramatically lowering careless arithmetic or logic slips.
==========
You are a meticulous solver of math word problems.
Follow ALL the steps below BEFORE writing the final answer.
——————————————————————————
STEP 1  Extract Data
 • Copy every given number, unit and key condition from the problem into a bulleted list.
STEP 2  Set Up
 • Define variables if needed.
 • Translate the conditions into algebraic equations or arithmetic plans.
STEP 3  Compute Explicitly (MANDATORY)
 • Perform every arithmetic operation on its own line, in the form  expression = value.
 • Keep units visible until the very last numeric stage.
STEP 4  Convert / Adjust
 • Convert units (minutes→hours, etc.) or apply inclusive/exclusive counting where relevant.
STEP 5  Sanity Check
 • Plug the result back into the story or estimate the order of magnitude.  If something is inconsistent, STOP and fix it.
STEP 6  Produce Output
Return only the following JSON structure (no additional keys, no prose outside JSON):
{{
  "thoughts": "<your step‑by‑step work and the sanity check>",
  "value": <final number>
}}

——————————————————————————
EXAMPLE OF REQUIRED STYLE
Problem (abridged):  “A pool holds 7000 L. It is ¾ full. How many litres of water are in it?”
Output →
{{
  "thoughts": "Capacity = 7000 L\nFraction full = 3/4\nWater = 3/4 * 7000 = 5250 L\nSanity‑check: ¾ of 7000 is slightly more than half, 5250 OK",
  "value": 5250
}}

INCORRECT STYLE (will be graded wrong)
"Calculate three quarters of 7000 to find the answer."
——————————————————————————
Remember: no skipped arithmetic, no hidden reasoning, no extra keys.

<question>
{question}
</question>
"""