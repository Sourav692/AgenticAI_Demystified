import asyncio
import shlex
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import AnyMessage, add_messages
from langgraph.checkpoint.memory import MemorySaver
from langgraph.prebuilt import tools_condition, ToolNode
from typing import Annotated, List
from typing_extensions import TypedDict

from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_openai import ChatOpenAI

from dotenv import load_dotenv
load_dotenv()

# MCP server launch config
server_params = StdioServerParameters(
    command="python",
    args=["weather_server.py"]
)

# LangGraph state definition
class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]


async def create_graph(session):
    # Load tools from MCP server
    tools = await load_mcp_tools(session)

    # LLM configuration (system prompt can be added later)
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    llm_with_tools = llm.bind_tools(tools)

    # Prompt template with user/assistant chat only
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that uses tools to get the current weather for a location."),
        MessagesPlaceholder("messages")
    ])

    chat_llm = prompt_template | llm_with_tools

    # Define chat node
    def chat_node(state: State) -> State:
        state["messages"] = chat_llm.invoke({"messages": state["messages"]})
        return state

    # Build LangGraph with tool routing
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

async def list_resources(session):
    """
    Fetches the list of available resources from the connected server
    and prints them in a user-friendly format.
    """
    try:
        resource_response = await session.list_resources()

        if not resource_response or not resource_response.resources:
            print("\nNo resources found on the server.")
            return

        print("\nAvailable Resources:")
        print("--------------------")
        for r in resource_response.resources:
            # The URI is the unique identifier for the resource
            print(f"  Resource URI: {r.uri}")
            # The description comes from the resource function's docstring
            if r.description:
                print(f"    Description: {r.description.strip()}")
        
        print("\nUsage: /resource <resource_uri>")
        print("--------------------")

    except Exception as e:
        print(f"Error fetching resources: {e}")

async def handle_resource(session, command: str) -> str | None:
    """
    Parses a user command to fetch a specific resource from the server
    and returns its content as a single string.
    """
    try:
        # The command format is "/resource <resource_uri>"
        parts = shlex.split(command.strip())
        if len(parts) != 2:
            print("\nUsage: /resource <resource_uri>")
            return None

        resource_uri = parts[1]

        print(f"\n--- Fetching resource '{resource_uri}'... ---")

        # Use the session's `read_resource` method with the provided URI
        response = await session.read_resource(resource_uri)

        if not response or not response.contents:
            print("Error: Resource not found or content is empty.")
            return None

        # Extract text from all TextContent objects and join them
        # This handles cases where a resource might be split into multiple parts
        text_parts = [
            content.text for content in response.contents if hasattr(content, "text")
        ]
        
        if not text_parts:
             print("Error: Resource content is not in a readable text format.")
             return None

        resource_content = "\n".join(text_parts)
        
        print("--- Resource loaded successfully. ---")
        return resource_content

    except Exception as e:
        print(f"\nAn error occurred while fetching the resource: {e}")
        return None
        
# Entry point
async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            agent = await create_graph(session)

            print("Weather MCP agent is ready.")
            # Add instructions for the new resource commands
            print("Type a question, or use one of the following commands:")
            print("  /resources                       - to list available resources")
            print("  /resource <resource_uri>         - to load a resource for the agent")

            while True:
                # This variable will hold the final message to be sent to the agent
                message_to_agent = ""
                
                user_input = input("\nYou: ").strip()
                if user_input.lower() in {"exit", "quit", "q"}:
                    break

                # --- Command Handling Logic ---
                if user_input.lower() == "/resources":
                    await list_resources(session)
                    continue # Command is done, loop back for next input

                elif user_input.startswith("/resource"):
                    # Fetch the resource content using our new function
                    resource_content = await handle_resource(session, user_input)

                    if resource_content:
                        # Ask the user what action to take on the loaded content
                        action_prompt = input("Resource loaded. What should I do with this content? (Press Enter to just save to context)\n> ").strip()
                        
                        # If user provides an action, combine it with the resource content
                        if action_prompt:
                            message_to_agent = f"""
                            CONTEXT from a loaded resource:
                            ---
                            {resource_content}
                            ---
                            TASK: {action_prompt}
                            """
                        # If user provides no action, create a default message to save the context
                        else:
                            print("No action specified. Adding resource content to conversation memory...")
                            message_to_agent = f"""
                            Please remember the following context for our conversation. Just acknowledge that you have received it.
                            ---
                            CONTEXT:
                            {resource_content}
                            ---
                            """
                    else:
                        # If resource loading failed, loop back for next input
                        continue
                
                else:
                    # For a normal chat message, the message is just the user's input
                    message_to_agent = user_input

                # --- Final agent invocation ---
                # All paths (regular chat or successful resource load) now lead to this single block
                if message_to_agent:
                    try:
                        response = await agent.ainvoke(
                            {"messages": [("user", message_to_agent)]},
                            config={"configurable": {"thread_id": "weather-session"}}
                        )
                        print("AI:", response["messages"][-1].content)
                    except Exception as e:
                        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
