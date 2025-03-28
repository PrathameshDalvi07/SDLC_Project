from pydantic import BaseModel, Field
from src.sdlc.state.state import State
import importlib
import subprocess
import webbrowser
import sys
import streamlit as st

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
        prompt = f"Summarize the user project idea {state['revised_query']} into a short, clear description of user stories that explain what the user wants to build and why, focusing on the key features and goals of the project."
        response = self.llm.invoke(prompt)
        messages = response
        initial_user_stories = response
        extra_message = "__Is the user story correct? (yes/no) If no, please specify the required changes.__"
        return {"messages":messages, "initial_user_stories": initial_user_stories, "extra_message": extra_message}
    
    def revised_user_stories(self, state: State):
        print("revised_user_stories --------------------------------------")
        prompt = f"Given the revised query {state['revised_query']}, update the user stories to reflect the changes while maintaining clarity and alignment with the project's goals. If needed, refer to the previous {state['initial_user_stories']} to ensure consistency and completeness. The updated user stories should remain concise and clearly describe what the user wants to build and why, focusing on the key features and objectives."
        response = self.llm.invoke(prompt)
        messages = response
        initial_user_stories = response
        extra_message = "__Does this revised user story accurately reflect the requirements? (yes/no) If no, please specify the required changes.__"
        return {"messages":messages, "initial_user_stories": initial_user_stories, "extra_message": extra_message, "human_feedback": "", "iterations": 0}
    
    def human_loop_product_owner_review(self, state: State):
        print("human_loop_product_owner_review --------------------------------------")
        pass

    def create_design_docs(self, state: State):
        print("create_design_docs --------------------------------------")
        return {"messages":"", "initial_user_stories": "", "extra_message": ""}
    
    def should_with_user_stories_continue(self, state: State):
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
        return {"generation": code_solution, "messages": messages, "iterations": iterations, "extra_message": "__Rechecking the code for accuracy and improvements.__"}
    
    def code_check(self, state: State):
        """
        Check code

        Args:
            state (dict): The current graph state

        Returns:
            state (dict): New key added to state, error
        """

        print("---CHECKING CODE---")

        # State
        messages = state["messages"]
        code_solution = state["generation"]
        iterations = state["iterations"]

        # Get solution components
        imports = code_solution.imports
        code = code_solution.code

        def install_module(module_name: str):
            """
            Install the module using pip.

            Args:
                module_name (str): The name of the module to install
            """
            subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])

        def check_imports(imports: str):
            """
            Check if the necessary modules are installed and install them if not.

            Args:
                imports (str): The import statements

            Raises:
                ImportError: If a module cannot be installed
            """
            for line in imports.split('\n'):
                if line.startswith('import') or line.startswith('from'):
                    module_name = line.split()[1]
                    if '.' in module_name:
                        module_name = module_name.split('.')[0]
                    if not importlib.util.find_spec(module_name):
                        try:
                            install_module(module_name)
                        except Exception as e:
                            raise ImportError(f"Module '{module_name}' is not available in the current environment and could not be installed. Error: {e}")

        # Check imports
        try:
            check_imports(imports)
            exec(imports)
        except Exception as e:
            print("---CODE IMPORT CHECK: FAILED---")
            error_message = [
                (
                    "user",
                    f"Your solution failed the import test. Here is the error: {e}. Reflect on this error and your prior attempt to solve the problem. (1) State what you think went wrong with the prior solution and (2) try to solve this problem again. Return the FULL SOLUTION. Use the code tool to structure the output with a prefix, imports, and code block:",
                )
            ]
            messages += error_message
            return {
                "generation": code_solution,
                "messages": messages,
                "iterations": iterations,
                "error": "yes",
                "extra_message": "__Provide feedback? (yes/no) If 'yes',  please specify the required changes and if 'no', the code will run in the web browser.__",
            }

        # Check execution
        try:
            combined_code = f"{imports}\n{code}"
            print(f"CODE TO TEST: {combined_code}")
            # Use a shared scope for exec
            global_scope = {}
            exec(imports, global_scope)  # Ensure imports are executed first
            exec(code, global_scope)     # Then execute the code
        except Exception as e:
            print("---CODE BLOCK CHECK: FAILED---")
            error_message = [
                (
                    "user",
                    f"Your solution failed the code execution test: {e}) Reflect on this error and your prior attempt to solve the problem. (1) State what you think went wrong with the prior solution and (2) try to solve this problem again. Return the FULL SOLUTION. Use the code tool to structure the output with a prefix, imports, and code block:",
                )
            ]
            messages += error_message
            return {
                "generation": code_solution,
                "messages": messages,
                "iterations": iterations,
                "error": "yes",
            }

        # No errors
        print("---NO CODE TEST FAILURES---")
        return {
            "generation": code_solution,
            "messages": messages,
            "iterations": iterations,
            "error": "no",
            "extra_message": "__Provide feedback? (yes/no) If 'yes',  please specify the required changes and if 'no', the code will run in the web browser.__",
        }
    
    def decide_to_finish(self, state: State):
        """
        Determines whether to finish.
        Args:
            state (dict): The current graph state
        Returns:
            str: Next node to call
        """
        error = state["error"]
        iterations = state["iterations"]

        if error == "no" or iterations == max_iterations:
            print("---DECISION: FINISH---")
            return "Code Review Human Feedback"
        else:
            print("---DECISION: RE-TRY SOLUTION---")
            return "Generate Code"
        
    def should_with_code_review_continue(self, state: State):
        input = state.get('human_feedback',None)
        print("should_continue--------------------------------------  ",input)
        if input == "Code Review Human Feedback":
            return "Revised Code"
        return "END"
        # return "Design Docs"

    def human_loop_code_review(self, state: State):
        print("human_loop_code_review --------------------------------------")
        pass

    def revised_code(self, state: State):
        print("revised_code --------------------------------------")
        """
        Generate a code solution
        Args:
            state (dict): The current graph state
        Returns:
            state (dict): New key added to state, generation
        """
        
        messages = state["initial_user_stories"].content
        iterations = state["iterations"]
        code_solution = self.code_gen_chain.invoke(f"Based on the feedback provided {state["messages"]}, update the existing code {state["generation"]} as needed. Ensure that the revised code correctly addresses the feedback while maintaining clarity, efficiency, and functionality.")

        messages = [
            (
                "assistant",
                f"{code_solution.prefix} || {code_solution.imports} \n{code_solution.code}",
            )
        ]
        iterations = iterations + 1
        return {"generation": code_solution, "messages": messages, "iterations": iterations, "extra_message": "__Any changes needed? (yes/no) If yes, specify. If no, the code will run in the browser.__"}

    def code_run(self, state: State):
        """
        Run code in the Streamlit app.
        Args:
            state (dict): The current graph state
        Returns:
            str: Next node to call
        """
        st.write("### 🏃 Running Code in Streamlit")

        code_solution = state["generation"]

        imports = code_solution.imports
        code = code_solution.code
        try:
            combined_code = f"{imports}\n{code}"
            print(f"CODE TO TEST: {combined_code}")

            result = subprocess.run(
                    ["python", "-c", combined_code],
                    capture_output=True,
                    text=True
                )
            st.code(result.stdout if result.stdout else result.stderr, language="python")
            print("Code executed successfully.")
            print("Output:                      ", result)
        except Exception as e:
            print("---iiiiiii---")
        return None
    
    def code_test(self, state: State):
        pass