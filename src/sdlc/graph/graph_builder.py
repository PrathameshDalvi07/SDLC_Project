from langgraph.graph import StateGraph, START,END, MessagesState
from langgraph.prebuilt import tools_condition,ToolNode
from langchain_core.prompts import ChatPromptTemplate
from src.sdlc.state.state import State
from src.sdlc.nodes.sdlc_node import SDLCNode
from langgraph.checkpoint.memory import MemorySaver

memory = MemorySaver()


class GraphBuilder:
    def __init__(self, model):
        self.model = model
        self.graph_builder = StateGraph(State)

    def sdlc_graph(self):
        self.sdlc_node = SDLCNode(self.model)

        self.graph_builder.add_node("User Stories",self.sdlc_node.generate_user_stories)
        self.graph_builder.add_node("Product Owner Review",self.sdlc_node.human_loop_product_owner_review)
        # self.graph_builder.add_node("Design Docs",self.sdlc_node.create_design_docs)
        self.graph_builder.add_node("Revised User Stories",self.sdlc_node.revised_user_stories)
        self.graph_builder.add_node("Generate Code",self.sdlc_node.generate_code)
        self.graph_builder.add_node("Check Code",self.sdlc_node.code_check)
        # self.graph_builder.add_node("Code Run",self.sdlc_node.code_run)
        # self.graph_builder.add_node("Code Test",self.sdlc_node.code_test)
        self.graph_builder.add_node("Code Review Human Feedback",self.sdlc_node.human_loop_code_review)
        self.graph_builder.add_node("Revised Code",self.sdlc_node.revised_code)

        self.graph_builder.add_edge(START,"User Stories")
        self.graph_builder.add_edge("User Stories","Product Owner Review")
        self.graph_builder.add_conditional_edges("Product Owner Review",self.sdlc_node.should_with_user_stories_continue)
        self.graph_builder.add_edge("Revised User Stories","Product Owner Review")
        # self.graph_builder.add_edge("Design Docs",END)
        

        self.graph_builder.add_edge("Generate Code","Check Code")
        self.graph_builder.add_conditional_edges("Check Code", self.sdlc_node.decide_to_finish,
        {
            "Code Review Human Feedback": "Code Review Human Feedback",
            "Generate Code": "Generate Code",
        },)
        self.graph_builder.add_conditional_edges("Code Review Human Feedback",self.sdlc_node.should_with_code_review_continue)
        self.graph_builder.add_edge("Revised Code","Code Review Human Feedback")


        # self.graph_builder.add_edge("Code Run","Code Test")
        # self.graph_builder.add_edge("Code Run",END)

    def setup_graph(self):
        self.sdlc_graph()
        return self.graph_builder.compile(checkpointer=memory, interrupt_before =["Product Owner Review","Code Review Human Feedback"])