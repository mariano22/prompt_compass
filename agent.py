from parsers import *

class Agent:
    def __init__(self, fn_chat):
        self.messages = []
        self.fn_chat = fn_chat

    async def send_user_message(self, prompt):
        self.messages.append({"role": "user", "content": prompt})
        new_message = await self.fn_chat(self.messages)
        self.messages.append(new_message)

    async def retry_until_parse(self, parse_fn, error_max_retries = 2, warnings_max_retries = 1):
        error_retries = 0
        warning_retries = 0
        last_valid = None
        for _ in range(error_max_retries + warnings_max_retries):
            last_content = self.last_content()
            parse_result = parse_fn(last_content)
            
            if parse_result.is_error():
                if error_retries == error_max_retries:
                    return last_valid
                error_retries += 1
            elif parse_result.warnings:
                if warning_retries == error_max_retries:
                    return last_valid
                warning_retries += 1
                last_valid = parse_result.get_value()
            else:
                return parse_result.get_value()
            await self.send_user_message(parse_result.get_feedback())
        return last_valid
        

    def last_content(self):
        return self.messages[-1]['content']

async def main():
    import tools
    from functools import partial
    import json
    from pydantic import BaseModel

    BIG_MODEL = "gpt-4.1"
    MEDIUM_MODEL = "gpt-4.1-mini"
    SMALL_MODEL = "gpt-4.1-nano"

    fn_llm = partial(tools.chat, model=MEDIUM_MODEL)
    
    class MyModel(BaseModel):
        name: str
        age: int

    prompt = f"""
    Parse the structured data from the provided text. Output a JSON respecting the provided pydantic model schema.

    <text>
    José Francisco de San Martín y Matorras[4]​ (Yapeyú, Imperio español; 25 de febrero de 1778 - Boulogne-sur-Mer, Francia; 17 de agosto de 1850)[5]​ fue un militar y político argentino, conocido por ser el libertador de la Argentina y Chile, además haber proclamado e impulsado la independencia de Perú. Es una de las figuras más trascendentes de las guerras de independencia hispanoamericanas junto a Simón Bolívar.
    </text>

    <pydantic model>
    {json.dumps(MyModel.model_json_schema(), indent=2)}
    </pydantic model>

    Only output the JSON.
    """

    class MyModelChecker(Parser):
        def __init__(self):
            super().__init__()
        
        def forward(self, model):
            result = ParserValue(value = model)
            if model.name != model.name.lower() :
                result.warn("\"name\" field must be entirely lowercase")
            return result

    json_parser = JSONParser()
    pydantic_parser = PydanticParser(MyModel)
    checker = MyModelChecker()

    def parse_function(x):
        x = json_parser(x)
        x = pydantic_parser(x)
        x = checker(x)
        return x

    agent = Agent(fn_llm)
    await agent.send_user_message(x)
    result = await agent.retry_until_parse(parse_function)
    print(result)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())