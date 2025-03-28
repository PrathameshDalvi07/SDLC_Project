from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph.message import AnyMessage, add_messages
from typing import Annotated

class State(TypedDict):
    query : str
    revised_query : str
    initial_user_stories : str
    extra_message: str
    human_feedback: str
    # messages: Annotated[list[AnyMessage], add_messages]
    messages: Annotated[list, add_messages]
    error: str
    generation: str
    iterations: int
    test_cases: str