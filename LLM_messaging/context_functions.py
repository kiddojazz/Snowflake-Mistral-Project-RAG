# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 09:45:13 2025

@author: olanr
"""

import sys
sys.path.append("..")
import time
import json
import io
from typing import Dict
#import pyodbc
import pandas as pd
#from openai_connection import get_gpt_response, openai_client
from mixtral_chat import MixtralAgents
from LLM_messaging.llm_context_and_format import (ChartReference, 
                                    LoadTableInfo,
                                    ContextTexts,
                                    NumReports,
                                    SqlQuery,
                                    GenerateCharts                 
                                    )
from pydantic import ValidationError
from mixtral_chat_utilities.mixtral_tools import get_dataframe_from_query


ma = MixtralAgents()

def get_chart_names():
    cr = ChartReference()
    chart_names = cr.load_chart_names()
    return chart_names

def get_chart_map():
    cr = ChartReference()
    chart_map = cr.load_map()
    return chart_map


def get_table_description(table_name: str):
    lti = LoadTableInfo(table_name)
    table_cols, sample_table_values = lti.load_info()
    
    table_description = ContextTexts.TABLE_DESCRIPTION.value.format(table_name = table_name, table_columns = table_cols, sample_column_values = sample_table_values)
    
    return table_description


def get_num_reports(user_prompt: str, table_name: str) -> str:
    table_description = get_table_description(table_name)

    gpt_context = ContextTexts.GET_NUM_REPORTS.value.format(
        user_prompt=user_prompt,
        table_description=table_description,
        output_format=json.dumps(NumReports.model_json_schema(), indent=2)
    )

    # Pass the gpt_context and use the correct output_format
    num_reports = ma.get_mixtral_response(
        text=user_prompt,
        context=gpt_context,
        output_format=NumReports  # Ensure output_format is the NumReports model
    )
    
    return num_reports



def get_num_reports2(user_prompt: str, table_name:str)->str:
    
    table_description = get_table_description(table_name)
        
    gpt_context = ContextTexts.GET_NUM_REPORTS.value.format(user_prompt = user_prompt, table_description = table_description)
    
    num_reports = get_gpt_response(text = user_prompt, 
                                   context = gpt_context, 
                                   response_format = NumReports, 
                                   openai_client = openai_client
                                   )
    return num_reports


def get_report_to_description_map(num_reports: NumReports)-> Dict:
    report_to_description_map = {}
    for report_collection in num_reports.reports:
        report_name = report_collection.report_name
        description = report_collection.description
        report_to_description_map[report_name] = description
    
    return report_to_description_map


def get_sql_from_description(user_prompt: str, report_statement: str, report_description: str):
    
    table_name = LoadTableInfo.default_table_name
    
    table_description = get_table_description(table_name)

    gpt_context = ContextTexts.GET_SQL_FROM_DESCRIPTION.value.format(report_statement = report_statement,
                                                                     report_description = report_description,
                                                                     table_description = table_description,
                                                                     output_format = json.dumps(SqlQuery.model_json_schema(), indent=2)
                                                                     )
    
    parsed_content = ma.get_mixtral_response(text = user_prompt,
                                        context = gpt_context,
                                        output_format = SqlQuery,
                                        )
    if "properties" in parsed_content:
        try:
            parsed_content = json.loads(parsed_content)
        except json.JSONDecodeError as e:
            print(f"Failed to decode the response as JSON: {e}")
            raise ValueError("Invalid JSON response from LLM.")
  
        parsed_content = parsed_content["properties"]

    try:    
        sql_query = SqlQuery.model_validate(parsed_content)
        sql_query.output = " ".join(sql_query.output.split("\n"))
        sql_query.output = sql_query.output.replace("\\", "")
        return " ".join(sql_query.output.split("\n"))
    except ValidationError as e:
        print(f"SQL Query Validation Error: \n{e}")
    

def get_sql_from_description2(user_prompt: str, report_statement: str, report_description: str):
    
    table_name = LoadTableInfo.default_table_name
    
    table_description = get_table_description(table_name)
    
    gpt_context = ContextTexts.GET_SQL_FROM_DESCRIPTION.value.format(report_statement = report_statement,
                                                                     report_description = report_description,
                                                                     table_description = table_description
                                                                     )
    
    sql_query = get_gpt_response(text = user_prompt, 
                                 context = gpt_context, 
                                 response_format = SqlQuery, 
                                 openai_client = openai_client
                                 )
    
    return " ".join(sql_query.output.split("\n"))    

def get_sqls_from_descriptions(user_prompt: str, report_to_description_map: Dict)-> Dict:
    topic_to_sql_map = {}
    
    for report_statement in report_to_description_map:
        report_description = report_to_description_map[report_statement]
        sql_query = get_sql_from_description(user_prompt, report_statement, report_description)
        topic_to_sql_map[report_statement] = sql_query
        
    return topic_to_sql_map


def get_topic_to_dataframe_map(topic_to_sql_map: Dict)-> Dict:
    topic_to_df_map = {}
    for topic in topic_to_sql_map:
        sql_query = topic_to_sql_map[topic]
        query_df = get_dataframe_from_query(sql_query)
        topic_to_df_map[topic] = query_df
    
    return topic_to_df_map


def generate_chart_info_from_df(user_prompt: str, df: pd.DataFrame, max_rows: int = 3):
    
    chart_names = get_chart_names()
    chart_map = get_chart_map()

    gpt_context = ContextTexts.GET_CHART_SUMMARY.value.format(user_prompt = user_prompt,
                                                               df_map = df.head(max_rows), 
                                                               df_stats = df.describe(include= "all"),    
                                                               chart_names = chart_names, 
                                                               chart_map = chart_map,
                                                              output_format = json.dumps(GenerateCharts.model_json_schema(), indent=2)
                                                               )
    
    charts_object = ma.get_mixtral_response(text = user_prompt,
                                        context = gpt_context,
                                        output_format = GenerateCharts,
                                        )
    
    return charts_object

def generate_all_charts_info(user_prompt: str, topic_to_dataframe_map: Dict)-> Dict:
    topic_to_chart_info = {}
    
    for topic in topic_to_dataframe_map:
        time.sleep(60)
        print(f"Getting charts for topic: {topic}")
        df = topic_to_dataframe_map[topic]
        
        if isinstance(df, pd.DataFrame):
            charts_object = generate_chart_info_from_df(user_prompt, df)
            
            topic_to_chart_info[topic] = charts_object
        
    return topic_to_chart_info
