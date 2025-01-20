# -*- coding: utf-8 -*-
"""
Created on Fri Jan  3 13:04:57 2025

@author: olanr
"""

import sys
sys.path.append("..")
from pages_markdowns import PagesMarkdowns

#from db_connection import create_connection, server, database, username, password

import streamlit as st

from LLM_messaging.context_functions import (get_topic_to_dataframe_map,
                                             get_num_reports,
                                             get_report_to_description_map,
                                             get_sqls_from_descriptions,
                                             generate_all_charts_info
                                             )

from pages_utilities.create_streamlit_chart import create_all_gpt_charts
from pages_utilities.streamlit_plots import reset_data_in_session_state
import time







        
def reload_data_from_database():

    if "topic_to_sql_map" in st.session_state and st.session_state.topic_to_sql_map != None:
        topic_to_sql_map = st.session_state.topic_to_sql_map
        
    else:
        st.warning("Please send a query before attempting to reload the data")
        return
    
    if "topic_to_chart_info" in st.session_state and st.session_state.topic_to_chart_info != None:
        topic_to_chart_info = st.session_state.topic_to_chart_info

    else:
        st.warning("Please send a query before attempting to reload the data")
        return
    
    st.session_state.topic_to_dataframe_map = get_topic_to_dataframe_map(topic_to_sql_map)
    topic_to_dataframe_map = st.session_state.topic_to_dataframe_map
    
    st.markdown("### Generated Dashboard:")
    create_all_gpt_charts(topic_to_dataframe_map, topic_to_chart_info)
    
    

def countdown_to_data_reset(num_minutes: int):
    num_seconds = num_minutes
    st.warning("countdown starting")
    while True:
        time.sleep(num_seconds)    
        reset_data_in_session_state()
        reload_data_from_database()
        st.warning(f"Data reloaded automatically after {num_seconds} seconds")
        # st.session_state.reload_data = True


def automatic_data_refresh(num_seconds: int):
    progress_text = "Time till refresh."
    
    my_bar = st.progress(0, text=progress_text)
    
    for seconds_elapsed in range(num_seconds):
        time.sleep(0.01)
        my_bar.progress(seconds_elapsed + 1, text=progress_text)
    time.sleep(1)
    my_bar.empty()
    
    reload_data_from_database()
    st.warning(f"Data reloaded automatically after {num_seconds} seconds")
    st.button("Rerun")
        

if __name__ == "__main__":

    reset_data_in_session_state()
    markdown_header, markdown_body = PagesMarkdowns.CHAT_MARKDOWN_HEADER.value, PagesMarkdowns.CHAT_MARKDOWN.value
    st.markdown(markdown_header)
    if st.toggle("Show Instructions"):
        st.markdown(markdown_body)
    
    user_prompt = st.chat_input("Type your query to generate the dashboard")
    
    if user_prompt:
        table_name = "MISTRALHEALTHDB.MEDICALRECORDDATAMART.FLATTENED_MEDICAL_RECORDS"
        
        num_reports = get_num_reports(user_prompt, table_name)
        
        report_to_description_map = get_report_to_description_map(num_reports)
        
        topic_to_sql_map = get_sqls_from_descriptions(user_prompt, report_to_description_map)
        st.session_state.topic_to_sql_map = topic_to_sql_map
        
        topic_to_dataframe_map = get_topic_to_dataframe_map(topic_to_sql_map)
        st.session_state.topic_to_dataframe_map = topic_to_dataframe_map
        
        topic_to_chart_info = generate_all_charts_info(user_prompt, topic_to_dataframe_map)
        st.session_state.topic_to_chart_info = topic_to_chart_info
        
        user_prompt = None
        
        st.markdown("### Generated Dashboard:")
        create_all_gpt_charts(topic_to_dataframe_map, topic_to_chart_info)

        st.write(topic_to_dataframe_map)
        
    elif st.button("Reload Data"):
        
        reset_data_in_session_state()
        reload_data_from_database()
        st.write(st.session_state.topic_to_dataframe_map)
        
    
    else:
        st.markdown("### Generated Dashboard:")
        try:
            #st.write(st.session_state.topic_to_chart_info)
            create_all_gpt_charts(st.session_state.topic_to_dataframe_map, st.session_state.topic_to_chart_info)
        except AttributeError as e:
            st.warning("Please enter a query.")
        
    
            
        
    

"""
Q: Generate dashboard for patients
"""
