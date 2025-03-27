from pydantic import BaseModel, Field
from src.sdlc.state.state import State

max_iterations = 3

class code(BaseModel):
    """Code output"""
    prefix: str = Field(description="Description of the problem and approach")
    imports: str = Field(description="Code block import statements")
    code: str = Field(description="Code block not including import statements")
    # description = "Schema for code solutions to questions about LCEL." 

class SDLCNode:
    def __init__(self,model):
        self.llm = model
        self.code_gen_chain = model.with_structured_output(code, include_raw=False)

    def generate_user_stories(self, state: State):
        print("generate_user_stories --------------------------------------")
        prompt = f"Summarize the user’s project idea {state['revised_query']} into a short, clear description of user stories that explain what the user wants to build and why, focusing on the key features and goals of the project."
        response = self.llm.invoke(prompt)
        messages = response
        initial_user_stories = response
        extra_message = "__Is the user story correct?(yes/no) If no Please Specify your changes__"
        return {"messages":messages, "initial_user_stories": initial_user_stories, "extra_message": extra_message}
    
    def revised_user_stories(self, state: State):
        print("revised_user_stories --------------------------------------")
        prompt = f"Summarize the user’s project idea {state['revised_query']} into a short, clear description of user stories that explain what the user wants to build and why, focusing on the key features and goals of the project."
        response = self.llm.invoke(prompt)
        messages = response
        initial_user_stories = response
        extra_message = "__Is this improved User story is correct?(yes/no)__"
        return {"messages":messages, "initial_user_stories": initial_user_stories, "extra_message": extra_message, "human_feedback": "", "iterations": 0}
    
    def human_loop_product_owner_review(self, state: State):
        print("human_loop_product_owner_review --------------------------------------")
        pass

    def create_design_docs(self, state: State):
        print("create_design_docs --------------------------------------")
        return {"messages":"", "initial_user_stories": "", "extra_message": ""}
    
    def should_continue(self, state: State):
        input = state.get('human_feedback',None)
        print("should_continue--------------------------------------  ",input)
        if input == "Revised User Stories":
            return "Revised User Stories"
        return "Generate Code"
        # return "Design Docs"
    
    def generate_code(self, state: State):
        """
        Generate a code solution
        Args:
            state (dict): The current graph state
        Returns:
            state (dict): New key added to state, generation
        """
        
        messages = state["initial_user_stories"].content
        iterations = state["iterations"]
        code_solution = self.code_gen_chain.invoke(f"Generate a code solution by User story {messages}")

        messages = [
            (
                "assistant",
                f"{code_solution.prefix} || {code_solution.imports} \n{code_solution.code}",
            )
        ]
        iterations = iterations + 1
        return {"generation": code_solution, "messages": messages, "iterations": iterations, "extra_message": ""}