import asyncio
import os
import json


from instructor import patch
from instructor.exceptions import InstructorRetryException
from pydantic import BaseModel, Field
import openai

from tools import *


openai_client = openai.AsyncOpenAI()
instructor_client = patch(openai_client)

async def openai_callback(messages, model):
    response = await openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
            )
    return response.choices[0].message.content


class MathSolution(BaseModel):
    """A math solution with step-by-step reasoning and final answer"""
    thoughts: str = Field(..., description="step-by-step solving of the problem")
    value_first_attempt: str = Field(..., description="A numerical answer or python evaluable expression without variables (only numbers and operations) or just numerical constant with the final answer to the math problem")
    reflect: str = Field(..., description="Analyse the thoughts and value_first_attempt for correctness. Determine if value_first_attempt is a numerical expression with only constants")
    value: str = Field(..., description="A numerical answer or python evaluable expression without variables (only numbers and operations) or just numerical constant with the final answer to the math problem")

async def instructor_callback(messages, model):
    #print('using'+model)
    return await instructor_client.chat.completions.create(
                model=model,
                messages=messages,
                response_model=MathSolution,
                temperature=0,
            )

async def call_llm(prompt, fn_llm, max_retries = 5):
    delay = 1
    for attempt in range(max_retries):
        try:
            messages = [{"role": "user", "content": prompt}]
            result = await fn_llm(messages)
            return result
        except Exception as e:
            if isinstance(e, InstructorRetryException):
                try:
                    return json.loads(e.last_completion.choices[0].message.tool_calls[0].function.arguments)
                except:
                    pass
            print(f"ATTEMPT {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff
            else:
                print("MAX RETRIES REACHED. RETURNING NONE =======")
                return None