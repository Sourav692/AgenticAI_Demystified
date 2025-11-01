import asyncio
from mcp import StdioServerParameters
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import tools_condition, ToolNode
from typing import Annotated, List
from typing_extensions import TypedDict

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

# Import the MultiServerMCPClient
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
load_dotenv()

# --- Multi-server configuration dictionary ---
# This dictionary defines all the servers the client will connect to
server_configs = {
    "weather": {
        "command": "python",
        "args": ["weather_server.py"],  # Your original weather server
        "transport": "stdio",
    },
    "tasks": {
        "command": "python",
        "args": ["task_server.py"], # The new task management server
        "transport": "stdio",
    }
}

# LangGraph state definition (remains the same)
class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]


# --- 'create_graph' now accepts the list of tools directly ---
def create_graph(tools: list):
    # LLM configuration (remains the same)
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    llm_with_tools = llm.bind_tools(tools)

    # --- Updated system prompt to reflect new capabilities ---
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant. You have access to tools for checking the weather and managing a to-do list. Use the tools when necessary based on the user's request."),
        MessagesPlaceholder("messages")
    ])

    chat_llm = prompt_template | llm_with_tools

    # Define chat node (remains the same)
    def chat_node(state: State) -> State:
        response = chat_llm.invoke({"messages": state["messages"]})
        return {"messages": [response]}

    # Build LangGraph with tool routing (remains the same)
    graph = StateGraph(State)
    graph.add_node("chat_node", chat_node)
    graph.add_node("tool_node", ToolNode(tools=tools))
    graph.add_edge(START, "chat_node")
    graph.add_conditional_edges("chat_node", tools_condition, {
        "tools": "tool_node",
        "__end__": END
    })
    graph.add_edge("tool_node", "chat_node")

    return graph.compile(checkpointer=MemorySaver())


# --- Main function now uses MultiServerMCPClient ---
async def main():
    # As per the error message, instantiate the client directly
    # The client will manage the server subprocesses internally
    client = MultiServerMCPClient(server_configs)
    
    # Get a single, unified list of tools from all connected servers
    all_tools = await client.get_tools()

    # Create the LangGraph agent with the aggregated list of tools
    agent = create_graph(all_tools)
    
    print("MCP Agent is ready (connected to Weather and Task servers).")

    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() in {"exit", "quit", "q"}:
            break

        try:
            response = await agent.ainvoke(
                {"messages": [("user", user_input)]},
                config={"configurable": {"thread_id": "multi-server-session"}}
            )
            print("AI:", response["messages"][-1].content)
        except Exception as e:
            print("Error:", e)


if __name__ == "__main__":
    asyncio.run(main())