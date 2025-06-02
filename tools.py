GLOBAL_RUN_CONFIG = dict()
def get_run_config():
    global GLOBAL_RUN_CONFIG
    return GLOBAL_RUN_CONFIG

def set_run_config(config):
    global GLOBAL_RUN_CONFIG
    GLOBAL_RUN_CONFIG = config

def build_datasets(dataset, count: int = 100, split: float = 0.7):
    train_count = int(count * split)
    test_count = count - train_count

    train_dataset = [dataset["train"][i] for i in range(train_count)]
    test_dataset = [dataset["train"][i] for i in range(-test_count, 0)]

    def parse_data(data):
        parsed_data = []
        for item in data:
            question, full_answer = item["question"], item["answer"]
            thoughts, _, answer = full_answer.partition("\n#### ")
            parsed_data.append({"question": question, "thoughts": thoughts, "answer": answer or None})
        return parsed_data

    train_data = parse_data(train_dataset)
    test_data = parse_data(test_dataset)

    return train_data, test_data

def pm(m):
    print(f"ROLE: {m['role']}\nCONTENT:\n{m['content']}")
    print("====== PRINT SEP ======")
    
def pms(ms):
    for m in ms:
        pm(m)

import os
import openai


openai_client = openai.AsyncOpenAI()

async def chat(messages, model, verbose):
    if verbose:
        pm(messages[-1])
    response = await openai_client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
            )
    res = { 'content': response.choices[0].message.content, 'role': response.choices[0].message.role }
    if verbose:
        pm(res)
    return res