import asyncio

from tqdm.asyncio import tqdm_asyncio
from functools import partial

from predictors import *

def configure(model, fn_name):
    predict_fn = partial(eval(fn_name), model=model)
    tag = fn_name + '-' + model
    return predict_fn, tag

async def evaluate(test_set, predict_fn, tag, max_concurrent_requests: int = 10):
    semaphore = asyncio.Semaphore(max_concurrent_requests)
    async def evaluate_item(item):
         async with semaphore:
             result = await predict_fn(item["question"])
             return evaluate_item_result(item, result)
    tasks = [evaluate_item(item) for item in test_set]
    results = []
    for f in tqdm_asyncio.as_completed(tasks):
        result = await f
        results.append(result)
    return {
        'tag': tag,
        'results': results,
    }

def calculate_pass_rate(results):
    total = len(results)
    passed = sum(1 for result in results if result["pass"])
    format_error = sum(1 for result in results if result["format_error"])
    api_error = sum(1 for result in results if result["api_error"])
    return {
        'pass_rate': (passed / total) * 100,
        'format_error_rate': (format_error / total) * 100,
        'api_error_rate': (api_error / total) * 100,
    }