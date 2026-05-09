from typing import Annotated, TypedDict
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import BaseMessage, HumanMessage
from langgraph.graph.message import add_messages
from src.autonomous_context_engine.mcp_server.server import query_documentation, execute_python_code

# 1. Define the Agent's State
class State(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]

# 2. Define the Tools
tools = [query_documentation, execute_python_code]
tool_node = ToolNode(tools)

# 3. Initialize the Model (Gemini 3.1 Flash) and Bind Tools
model = ChatGoogleGenerativeAI(model="gemini-3.1-flash-lite").bind_tools(tools)

# 4. Define the Logic
def should_continue(state: State):
    messages = state['messages']
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END

def call_model(state: State):
    messages = state['messages']
    response = model.invoke(messages)
    return {"messages": [response]}

# 5. Build the Graph
workflow = StateGraph(State)

workflow.add_node("agent", call_model)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

app = workflow.compile()

# 6. Test Execution
if __name__ == "__main__":
    inputs = {"messages": [HumanMessage(content="What are the specific IP settings for the gateway server in the Process Data Acquisition manual?")]}
    for output in app.stream(inputs):
        for key, value in output.items():
            print(f"--- Node: {key} ---")
            if "messages" in value:
                print(value["messages"][-1].content)