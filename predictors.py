from functools import partial

from llm import *
from prompts import *
from tools import *

def parse_int(result):
    result = result.replace(",","")
    result = result.replace("$","")
    result = result[:result.find('.')] if '.' in result else result
    result = result[:result.find(':')] if ':' in result else result
    while '=' in result:
        result = result[result.find('=')+1:] if '=' in result else result
    try:
        return int(result)
    except Exception as e:
        print(f"Exception: {e}")
        return None

def post_processing(prompt, result, model=None):
    final_result = {
        'prompt': prompt,
        'response': result,
        'predicted': None,
        'predicted_thoughts': None,
    }
    
    if model is not None:
        final_result['model']=model
    
    if result is None:
        return final_result

    if not isinstance(result,str) and not isinstance(result,dict):
        final_result['response'] = result.model_dump_json()
        
    
    if hasattr(result, 'value'):
        final_result['predicted'] = result.value
    elif isinstance(result, dict):
        final_result['predicted'] = result.get('value',None)
    else:
        assert isinstance(result, str), str(result)
        final_result['predicted'] = result

    if isinstance(final_result['predicted'],str):
        try:
            final_result['predicted']=eval(final_result['predicted'])
        except Exception as e:
            final_result['predicted']=parse_int(final_result['predicted'])
    
    
    if hasattr(result, 'thoughts'):
        final_result['predicted_thoughts'] = result.thoughts
    
    if isinstance(result, dict) and 'thoughts' in result:
        final_result['predicted_thoughts'] = result['thoughts']
    
    return final_result

async def predict_naive(question, model):
    prompt = make_naive_prompt(question)
    result = await call_llm(prompt, partial(openai_callback, model=model))
    final_result = post_processing(prompt, result)
    return final_result

async def predict_cot(question, model):
    prompt = make_cot_prompt(question)
    result = await call_llm(prompt, partial(instructor_callback,model=model))
    final_result = post_processing(prompt, result, model=model)
    return final_result

async def predict_cot_fixed_examples(question):
    prompt = make_cot_fixed_examples_prompt(question, random.sample(training,k=12))
    result = await call_llm(prompt, instructor_callback)
    final_result = post_processing(prompt, result)
    return final_result

async def predict_cot_learned_examples(question, result_examples):
    ids = random.sample(range(len(results_examples)),k=6)
    current_examples = [results_examples[i] for i in ids]
    prompt = make_cot_fixed_examples_prompt(question, current_examples)
    result = await call_llm(prompt, instructor_callback)
    final_result = post_processing(prompt, result)
    return final_result

def evaluate_item_result(item, result):
    answer_int = int(item["answer"].replace(",", ""))
    api_error = result["response"] is None
    format_error = not api_error and result["predicted"] is None
    return {
        "api_error": api_error,
        "format_error": format_error,
        "pass": answer_int == result["predicted"],
        **result,
        **item,
    }