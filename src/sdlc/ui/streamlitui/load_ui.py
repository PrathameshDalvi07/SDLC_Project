import streamlit as st
import os
from langchain_core.messages import AIMessage,HumanMessage
from src.sdlc.ui.uiconfigfile import Config

class LoadStreamlitUI:
    def __init__(self):
        self.config =  Config() # config
        self.user_controls = {}

    def initialize_session(self):
        return {
        "current_step": "requirements",
        "requirements": "",
        "user_stories": "",
        "po_feedback": "",
        "generated_code": "",
        "review_feedback": "",
        "decision": None
    }
  


    def load_streamlit_ui(self):
        st.set_page_config(page_title= self.config.get_page_title(), layout="wide")
        st.header(self.config.get_page_title())
        st.markdown(self.config.get_page_description())
        st.session_state.timeframe = ''
        st.session_state.IsFetchButtonClicked = False
        st.session_state.IsSDLC = False
        
        with st.sidebar:
            # Get options from config
            llm_options = self.config.get_llm_options()

            # LLM selection
            self.user_controls["selected_llm"] = st.selectbox("Select LLM", llm_options)

            if self.user_controls["selected_llm"] == 'Groq':
                model_options = self.config.get_groq_model_options()
                self.user_controls["selected_groq_model"] = st.selectbox("Select Model", model_options)

                # self.user_controls["GROQ_API_KEY"] = st.session_state["GROQ_API_KEY"] = st.text_input("API Key",
                                                                                                    #   type="password")
                
                self.user_controls["GROQ_API_KEY"] = "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"
                # Validate API key
                if not self.user_controls["GROQ_API_KEY"]:
                    st.warning("⚠️ Please enter your GROQ API key to proceed. Don't have? refer : https://console.groq.com/keys ")
        
        return self.user_controls