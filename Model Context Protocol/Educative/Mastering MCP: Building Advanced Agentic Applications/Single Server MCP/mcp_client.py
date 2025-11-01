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

async def list_prompts(session):
    """
    Fetches the list of available prompts from the connected server
    and prints them in a user-friendly format.
    """
    try:
        prompt_response = await session.list_prompts()

        if not prompt_response or not prompt_response.prompts:
            print("\nNo prompts were found on the server.")
            return

        print("\nAvailable Prompts and Their Arguments:")
        print("---------------------------------------")
        for p in prompt_response.prompts:
            print(f"Prompt: {p.name}")
            if p.arguments:
                arg_list = [f"<{arg.name}>" for arg in p.arguments]
                print(f"  Arguments: {' '.join(arg_list)}")
            else:
                print("  Arguments: None")
        
        print("\nUsage: /prompt <prompt_name> \"arg1\" \"arg2\" ...")
        print("---------------------------------------")

    except Exception as e:
        print(f"Error fetching prompts: {e}")

async def handle_prompt(session, command: str) -> str | None:
    """
    Parses a user command to invoke a specific prompt from the server,
    then returns the generated prompt text.
    """
    try:
        parts = shlex.split(command.strip())
        if len(parts) < 2:
            print("\nUsage: /prompt <prompt_name> \"arg1\" \"arg2\" ...")
            return None

        prompt_name = parts[1]
        user_args = parts[2:]

        # Get available prompts from the server to validate against
        prompt_def_response = await session.list_prompts()
        if not prompt_def_response or not prompt_def_response.prompts:
            print("\nError: Could not retrieve any prompts from the server.")
            return None
        
        # Find the specific prompt definition the user is asking for
        prompt_def = next((p for p in prompt_def_response.prompts if p.name == prompt_name), None)

        if not prompt_def:
            print(f"\nError: Prompt '{prompt_name}' not found on the server.")
            return None

        # Check if the number of user-provided arguments matches what the prompt expects
        if len(user_args) != len(prompt_def.arguments):
            expected_args = [arg.name for arg in prompt_def.arguments]
            print(f"\nError: Invalid number of arguments for prompt '{prompt_name}'.")
            print(f"Expected {len(expected_args)} arguments: {', '.join(expected_args)}")
            return None
        
        # Build the argument dictionary
        arg_dict = {arg.name: val for arg, val in zip(prompt_def.arguments, user_args)}

        # Fetch the prompt from the server using the validated name and arguments
        prompt_response = await session.get_prompt(prompt_name, arg_dict)
        
        # Extract the text content from the response
        prompt_text = prompt_response.messages[0].content.text

        print("\n--- Prompt loaded successfully. Preparing to execute... ---")
        # Return the fetched text to be used by the agent
        return prompt_text

    except Exception as e:
        print(f"\nAn error occurred during prompt invocation: {e}")
        return None

# Entry point
async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            agent = await create_graph(session)

            print("Weather MCP agent is ready.")
            # Add instructions for the new prompt commands
            print("Type a question, or use one of the following commands:")
            print("  /prompts                           - to list available prompts")
            print("  /prompt <prompt_name> \"args\"...  - to run a specific prompt")

            while True:
                # This variable will hold the final message to be sent to the agent
                message_to_agent = ""
                
                user_input = input("\nYou: ").strip()
                if user_input.lower() in {"exit", "quit", "q"}:
                    break

                # --- Command Handling Logic ---
                if user_input.lower() == "/prompts":
                    await list_prompts(session)
                    continue # Command is done, loop back for next input

                elif user_input.startswith("/prompt"):
                    # The handle_prompt function now returns the prompt text or None
                    prompt_text = await handle_prompt(session, user_input)
                    if prompt_text:
                        message_to_agent = prompt_text
                    else:
                        # If prompt fetching failed, loop back for next input
                        continue
                
                else:
                    # For a normal chat message, the message is just the user's input
                    message_to_agent = user_input

                # Final agent invocation
                # All paths (regular chat or successful prompt) now lead to this single block
                if message_to_agent:
                    try:
                        # LangGraph expects a list of messages
                        response = await agent.ainvoke(
                            {"messages": [("user", message_to_agent)]},
                            config={"configurable": {"thread_id": "weather-session"}}
                        )
                        print("AI:", response["messages"][-1].content)
                    except Exception as e:
                        print("Error:", e)

if __name__ == "__main__":
    asyncio.run(main())
