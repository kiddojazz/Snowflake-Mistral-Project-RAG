import os
import json
import io
from dotenv import load_dotenv
from pydantic import BaseModel
from groq import Groq
import groq
from typing import Dict
from enum import Enum
from mixtral_chat_utilities.mixtral_context import (ContextTexts,
                                                    PromptTexts,
                                                    SqlPrompt,
                                                    PromptGenerator,
                                                    StreamlitBot
                                                    )
from mixtral_chat_utilities.mixtral_tools import get_dataframe_from_query
import json
from pydantic import ValidationError
import pandas as pd
import time


load_dotenv()

client = Groq(
    # This is the default and can be omitted
    api_key=os.environ.get("GROQ_API_KEY"),
)
    
class MixtralAgents:

    def __init__(self):
        pass
    
    def sql_query_agent(self, text: str, client: Groq, temperature: float= 0.0):

        prompt_context = ContextTexts.TABLE_ASSISTANT.value.format(output_format = json.dumps(SqlPrompt.model_json_schema(), indent = 2)) 
        contextual_prompt = PromptTexts.TABLE_ASSISTANT.value.format(user_prompt = text)
            
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt_context
                    },
                {
                    "role": "user",
                    "content": contextual_prompt,
                    }
            ],
            model="mixtral-8x7b-32768",
            temperature = temperature,
            stream = False,
            response_format = {"type": "json_object"}
        )
        parsed_content = json.loads(chat_completion.choices[0].message.content)

        if "output" in parsed_content:
            parsed_content = parsed_content["output"]

        try:
            validated_response = SqlPrompt.model_validate(parsed_content)
            return validated_response
        except ValidationError as e:
            print(f"SQL Query Validation Error: \n{e}")
        

    
    def prompt_agent(self, text: str, client: Groq, cached_context: Dict = {}, temperature: float= 0.0):

        prompt_context = ContextTexts.NOMINAL_CONTEXT.value.format(output_format = json.dumps(PromptGenerator.model_json_schema(), indent = 2)) 
        contextual_prompt = PromptTexts.NOMINAL_PROMPT_ASSISTANT.value.format(user_prompt = text)
        
        if cached_context:
            user_previous_prompts = list(cached_context.keys())
            previous_responses = list(cached_context.values())
            prompt_context = ContextTexts.PREVIOUS_CONTEXT.value.format(user_previous_prompts = user_previous_prompts,
                                                                        previous_responses = previous_responses,
                                                                        output_format = json.dumps(PromptGenerator.model_json_schema(), indent = 2)
                                                                        )
            contextual_prompt = PromptTexts.PROMPT_ASSISTANT.value.format(user_prompt = text)
        
            
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt_context
                    },
                {
                    "role": "user",
                    "content": contextual_prompt,
                    }
            ],
            model="mixtral-8x7b-32768",
            temperature = temperature,
            stream = False,
            response_format = {"type": "json_object"}
        )
        parsed_content = json.loads(chat_completion.choices[0].message.content)

        if "output" in parsed_content:
            parsed_content = parsed_content["output"]

        try:
            validated_response = PromptGenerator.model_validate(parsed_content)
            return validated_response
        except ValidationError as e:
            print(f"SQL Query Validation Error: \n{e}")
            
    

    def streamlit_agent(self, text: str, client: Groq, df: pd.DataFrame, cached_context: Dict = {}, temperature: float= 0.0):
        if len(df) <= 0:
            return "DataFrame is empty!"

        df_buffer = io.StringIO()
        df.info(buf=df_buffer)
        prompt_context = ContextTexts.STREAMLIT_NOMINAL_CONTEXT.value.format(output_format = json.dumps(StreamlitBot.model_json_schema(), indent = 2),
                                                                             df = df.sample(20),
                                                                             df_info = df_buffer.getvalue(),
                                                                             df_description = df.describe(include = "all")
                                                                             ) 
        contextual_prompt = PromptTexts.STREAMLIT_NOMINAL_ASSISTANT.value.format(user_prompt = text)
        
        if cached_context:
            user_previous_prompts = list(cached_context.keys())
            previous_responses = list(cached_context.values())
            prompt_context = ContextTexts.STREAMILT_PREVIOUS_CONTEXT.value.format(user_previous_prompts = user_previous_prompts,
                                                                                  previous_responses = previous_responses,
                                                                                  output_format = json.dumps(StreamlitBot.model_json_schema(), indent = 2),
                                                                                  df = df.sample(20),
                                                                                  df_info = df_buffer.getvalue(),
                                                                                  df_description = df.describe(include = "all")
                                                                                  )
            contextual_prompt = PromptTexts.STREAMLIT_ASSISTANT.value.format(user_prompt = text)

        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": prompt_context
                    },
                {
                    "role": "user",
                    "content": contextual_prompt,
                    }
            ],
            model="mixtral-8x7b-32768",
            temperature = temperature,
            stream = False,
            response_format = {"type": "json_object"}
        )
        parsed_content = json.loads(chat_completion.choices[0].message.content)

        if "output" in parsed_content:
            parsed_content = parsed_content["output"]

        try:
            validated_response = StreamlitBot.model_validate(parsed_content)
            return validated_response
        except ValidationError as e:
            print(f"SQL Query Validation Error: \n{e}")
    
    
    def get_mixtral_response(self, text: str,
                             context: str,
                             output_format: BaseModel,
                             temperature: float= 0.0,
                             client: Groq = client,
                             retry_seconds: int = 30,
                             max_retries: int = 3
                             ):
        num_retries = 0

        while num_retries < max_retries:
            try:            
                chat_completion = client.chat.completions.create(
                    messages=[
                        {
                            "role": "system",
                            "content": context
                            },
                        {
                            "role": "user",
                            "content": text,
                            }
                    ],
                    model="mixtral-8x7b-32768",
                    temperature = temperature
                )

            except groq.RateLimitError as e:
                print(f"You have hit the rate limit. Waiting {retry_seconds} seconds")
                time.sleep(retry_seconds)

            num_retries += 1

        parsed_content = chat_completion.choices[0].message.content
        print(f"{parsed_content = }")
        if "properties" in parsed_content:
            return parsed_content

        if "output" in parsed_content:
            parsed_content = parsed_content["output"]

        try:
            parsed_content = json.loads(parsed_content)

        except json.JSONDecodeError:
            raise ValueError("Failed to decode the response as JSON. Please check the format.")

        try:    
            validated_response = output_format.model_validate(parsed_content)
            return validated_response
        except ValidationError as e:
            print(f"SQL Query Validation Error: \n{e}")


    def get_mixtral_response2(self, text: str, client: Groq, cached_context: Dict = {}, temperature: float= 0.0):

        if cached_context:
            user_previous_prompts = list(cached_context.keys())
            previous_responses = list(cached_context.values())
            text = ContextTexts.PREVIOUS_CONTEXT.value.format(user_previous_prompts = user_previous_prompts,
                                                              previous_responses = previous_responses,
                                                              new_prompt = text
                                                              )
        
            
        chat_completion = client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "you are a helpful assistant."
                    },
                {
                    "role": "user",
                    "content": text,
                    }
            ],
            model="mixtral-8x7b-32768",
            temperature = temperature
        )

        return chat_completion.choices[0].message.content


    def parse_agent_response(self, sql_response: SqlPrompt):
        if sql_response.sql_query == "null":
            return sql_response.normal_response
        sql_query = sql_response.sql_query

        df = get_dataframe_from_query(sql_query)
        return df
        


class ResponseCache:

    def __init__(self, cache_max: int = 3):
        self.cache_max = cache_max
        self.current_cache = 0
        self._responses = {}
        
    def store_response(self, query, response):
        self.current_cache += 1
        if self.current_cache <= self.cache_max:
            self._responses[query] = response
            return
        
        self.current_cache -= 1
        self._responses.pop(list(self.responses.keys())[0])
        self._responses[query] = response

    @property
    def responses(self):
        return list(self._responses.values())

    @property
    def queries(self):
        return list(self._responses.keys())

    @property
    def get_conversation(self)-> Dict:
        return self._responses
    
    def get_last_n_responses(self, n: int = 3):
        query_list = list(self._responses.keys())
        response_list = list(self._responses.valus())

        return dict(zip(query_list[n:], response_list[n:]))
        
    def clear_cache(self):
        self.current_cache = 0
        self._responses = {}
            


if __name__ == "__main__":
    text = "Hello, how are you doing today?"
    sql_text = "I need information about the patient with the highest heart rate"

    ma = MixtralAgents()
    
    response = ma.get_mixtral_response(text, client)
    new_prompt = ma.prompt_agent(text, client)

    new_sql_prompt = ma.prompt_agent(sql_text, client)
    sql_response = ma.sql_query_agent(new_sql_prompt, client)

    sql_df = ma.parse_agent_response(sql_response)
    
    sample_df = pd.DataFrame(data = {"A": [1,2,3], "B": [2,3,4], "C": [5,6,7]})
    streamlit_response = ma.streamlit_agent(sql_text, client, df=sql_df)
    print(response)
    print(new_prompt)
    print(sql_response)
    print(streamlit_response)
