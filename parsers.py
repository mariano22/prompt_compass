from pydantic import ValidationError
from abc import ABC
from json import JSONDecodeError
import json

def prompt_create_tag(tag, value, **kwargs):
    kwargs_str = ''.join(f" {k}={v}" for k,v in kwargs.items())
    return f"<{tag}{kwargs_str}>\n{value}\n</{tag}>"

def parse_markers(s, start_marker, end_marker):
    start_pos = s.find(start_marker)
    if start_pos == -1:
        return s
    start_pos +=  len(start_marker)
    parsed = s[start_pos:]
    end_pos = parsed.find(end_marker)
    parsed = parsed[:end_pos]
    return parsed

class ParserValue(ABC):
    def __init__(self, value=None, error=None):
        self.error = error
        self.warnings = []
        self.value = value

    def warn(self, warning):
        self.warnings.append(warning)

    def is_error(self):
        return bool(self.error)

    def get_value(self):
        return self.value

    def get_feedback(self):
        if self.error:
            header = "An error occurred while parsing the response. Please reformulate your previous response, taking into account the following error message:"
            return header + "\n" + self.error+ "\n First reason about the possible causes of the error. Then, reformulate the output."
        warning_text = ""
        if self.warnings:
            header = f"{len(self.warnings)} warnings occurred while parsing the response. Please reformulate your previous response, taking the following warnings into account:"
            warning_strs = [ prompt_create_tag("warning", warning,id=i) for i,warning in enumerate(self.warnings) ]
            warnings = '\n'.join(warning_strs)
            return header + "\n" + warnings 
        

class Parser(ABC):
    def __call__(self, value):
        if not isinstance(value, ParserValue):
            value = ParserValue(value = value)

        if value.is_error():
            return value
        
        result = self.forward(value.get_value())
        
        if not result.is_error():
            result.warnings = value.warnings + result.warnings
    
        return result

class JSONParser(Parser):
    def forward(self, raw_str):
        try:
            raw_str = parse_markers(raw_str, start_marker = "```json", end_marker = "```")
            parsed = json.loads(raw_str)
            return ParserValue(value = parsed)
        except JSONDecodeError as e:
            error_msg = f"JSONDecodeError: error parsing string as JSON:\"{raw_str}\". Details:\n{str(e)}"
            return ParserValue(error = error_msg)

class PydanticParser(Parser):
    def __init__(self, pydantic_model):
        super().__init__()
        self.pydantic_model = pydantic_model
    
    def forward(self, some_json):
        try:
            pydantic_parsed = self.pydantic_model(**some_json)
            return ParserValue(value = pydantic_parsed)
        except ValidationError as e:
            lines = str(e).splitlines()
            cleaned_lines = [line for line in lines if "For further information visit" not in line]
            error_msg = "ValidationError: occurred while parsing the provided JSON with the given Pydantic schema."
            error_msg += "\n\n" + prompt_create_tag("json_to_parse", json.dumps(some_json, indent=2))
            error_msg += "\n\n" + prompt_create_tag("model_json_schema", json.dumps(self.pydantic_model.model_json_schema(), indent=2))
            error_msg += "\n\n" + prompt_create_tag("details", '\n'.join(cleaned_lines))
            return ParserValue(error = error_msg)

