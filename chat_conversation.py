import sys
sys.path.append("..")
import streamlit as st
from mixtral_chat import MixtralAgents, client, ResponseCache
import pandas as pd
from typing import Union, Tuple
from pages_markdowns import PagesMarkdowns


ma = MixtralAgents()
rc = ResponseCache()

class ChatInterface:

    def __init__(self, markdown: Tuple, chat_key = "main"):
        self.chat_key = chat_key
        
        self.markdown_header, self.markdown_body = markdown
        st.markdown(self.markdown_header)
        
        self.see_instructions = st.toggle("View Instructions")
        if self.see_instructions:
            st.markdown(self.markdown_body)
            
        st.divider()

        
    def generate_dataframe_from_prompt(self)->Union[pd.DataFrame, str]:
        prompt = st.chat_input("Say something", key = self.chat_key)
        if prompt:
            st.write(f"You: {prompt}")

            new_sql_prompt = ma.prompt_agent(prompt, client)

            sql_response = ma.sql_query_agent(new_sql_prompt, client)

            df_or_text = ma.parse_agent_response(sql_response)
    
            self.update_current_dataframe(df_or_text)

            st.write(df_or_text)

            return df_or_text


    def update_current_dataframe(self, df_or_text: Union[pd.DataFrame, str]):
        if isinstance(df_or_text, Union[pd.DataFrame, pd.Series]):
            st.session_state.current_dataframe = df_or_text
            return
        st.warning("Please use this feature to generate tables only")


class SideChatInterface:

    def __init__(self, bot_name, chat_key = "side"):
        self.side_chat_activated = st.toggle("Activate Sidebar")
        self.current_prompt = ""
        self.current_response = ""
        self.bot_name = bot_name
        self.chat_key = chat_key

        self.rc = ResponseCache()
        self.rc.clear_cache()
        
        if "current_dataframe" in st.session_state:
            self.chat_df = st.session_state.current_dataframe
        
        pass
        
    def converse_with_streamlit_bot(self):    
        with st.sidebar:
            sidechat_messages = st.container(height = 500)
            if prompt := st.chat_input("Say something", key = self.chat_key):
                # Type human message in chat
                sidechat_messages.chat_message("user").write(prompt)
                cached_context = self.rc.get_conversation
                self.current_prompt = prompt

                # Retrieve the LLM response to human message
                bot_response = ma.streamlit_agent(self.current_prompt, client, self.chat_df, cached_context)

                # Type Bot message using LLM response
                self.current_response = bot_response.bot_response
                #self.sidechat_bot.add_text(self.current_response)
                sidechat_messages.chat_message(self.bot_name).write(self.current_response)

                # Store prompt and response in Cache
                self.rc.store_response(self.current_prompt, self.current_response)


    def sidechat_conversation(self):
        if self.side_chat_activated:
            st.write(st.session_state.current_dataframe)
            self.converse_with_streamlit_bot()
            

    
if __name__ == "__main__":
    bot_name = "Jarvis"
    markdown_header = PagesMarkdowns.CHAT_MARKDOWN_HEADER.value
    page_markdown = PagesMarkdowns.CHAT_MARKDOWN.value

    main_chat = ChatInterface(markdown = (markdown_header,page_markdown))

    main_chat.generate_dataframe_from_prompt()

    if "current_dataframe" in st.session_state:
        
        side_chat = SideChatInterface(bot_name)
    
        side_chat.sidechat_conversation()
            
        
    """
    Give me information about women in their late 60s
    """
        
