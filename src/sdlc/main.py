import streamlit as st
from src.sdlc.ui.streamlitui.load_ui import LoadStreamlitUI
from src.sdlc.LLMS.groq_llm import GroqLLM
from src.sdlc.graph.graph_builder import GraphBuilder
from src.sdlc.ui.streamlitui.display_result import DisplayResultStreamlit

# MAIN Function START
def load_sdlc_app():

    ui = LoadStreamlitUI()
    user_input = ui.load_streamlit_ui()

    if not user_input:
        st.error("Error: Failed to load user input from the UI.")
        return

    if st.session_state.IsFetchButtonClicked:
        user_message = st.session_state.timeframe 
    else :
        user_message = st.chat_input("Specify project requirements:")

    if user_message:
            try:
                obj_llm_config = GroqLLM(user_controls_input=user_input)
                model = obj_llm_config.get_llm_model()
                
                if not model:
                    st.error("Error: LLM model could not be initialized.")
                    return

                graph_builder = GraphBuilder(model)
                try:
                    graph = graph_builder.setup_graph()
                    DisplayResultStreamlit(graph,user_message).display_result_on_ui()
                except Exception as e:
                    st.error(f"Error: Graph setup failed - {e}")
                    return
                

            except Exception as e:
                 raise ValueError(f"Error Occurred with Exception : {e}")
            

        

   

    