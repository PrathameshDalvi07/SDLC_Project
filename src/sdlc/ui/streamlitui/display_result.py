import uuid
import streamlit as st
from langchain_core.messages import HumanMessage,AIMessage
from src.sdlc.state.state import State

# st.session_state.messages = []
thread = str(uuid.uuid4())
config = {"configurable": { "thread_id": thread }}

class DisplayResultStreamlit:
    def __init__(self,graph,user_message):
        self.graph = graph
        self.user_message = user_message

    def display_result_on_ui(self):
        graph = self.graph
        user_message = self.user_message
        state = graph.get_state(config)
        messages = {'query':[("user", user_message)], 'messages': [("user", user_message)],"initial_user_stories":"", "extra_message": "", "human_feedback": "", "revised_query": user_message, "iterations" : 0, "generation": ""}

        if state.next != ():
            if  state.next[0] == 'Product Owner Review':
                if user_message != 'yes':
                    # st.session_state.messages.append(HumanMessage(content=user_message))
                    with st.chat_message("user"):
                        st.write(user_message)
                    messages = {'messages':"", "revised_query": user_message, "human_feedback": "Revised User Stories"}
                    graph.update_state(config, messages)
                messages = None

        # for msg in st.session_state.messages:
        #     if msg.type == 'human':
        #         with st.chat_message("user"):
        #             st.write(msg.content)
        #     elif msg.type == 'ai':
        #         with st.chat_message("assistant"):
        #             st.write(msg.content) 

        events = graph.stream(messages,config, stream_mode="values")
        for event in events:
            # if messages is not None:
            #     st.session_state.messages.append(event['messages'][-1])
            if event['messages'][-1].type == 'human':
                if event['messages'][-1].content:
                    with st.chat_message("user"):
                        st.write(event['messages'][-1].content)
            elif event['messages'][-1].type == 'ai':
                with st.chat_message("assistant"):
                    if event['generation']:
                        msg = event['messages'][-1].content.split("||")
                        prefix = msg[0]
                        st.write(prefix)
                        code = msg[1]
                        st.code(code, language="python")
                    else:
                        st.write(event['messages'][-1].content)
                if event['extra_message']:
                    with st.chat_message("assistant"):
                        st.write(event['extra_message'])
