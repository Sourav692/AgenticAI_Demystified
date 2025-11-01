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

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.schema import HumanMessage

from langchain_mcp_adapters.tools import load_mcp_tools


# MCP server launch config
server_params = StdioServerParameters(command="python", args=["mcp_server.py"])

# LangGraph state definition
class State(TypedDict):
    messages: Annotated[List[AnyMessage], add_messages]


async def create_graph(session):
    tools = await load_mcp_tools(session)
    llm = ChatOpenAI(model="gpt-4", temperature=0)
    llm_with_tools = llm.bind_tools(tools)

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", "You are a helpful assistant that uses tools to explore Wikipedia."),
        MessagesPlaceholder("messages")
    ])

    chat_llm = prompt_template | llm_with_tools

    def chat_node(state: State) -> State:
        state["messages"] = chat_llm.invoke({"messages": state["messages"]})
        return state

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
    try:
        response = await session.list_resources()
        if not response or not response.resources:
            print("No resources found on the server.")
            return

        print("\nAvailable Resources:")
        for i, r in enumerate(response.resources, 1):
            print(f"[{i}] {r.name}")
        print("\nUse: /resource <name> to view its content.")
    except Exception as e:
        print("Failed to list resources:", e)

async def handle_resource(session, command):
    parts = shlex.split(command.strip())
    if len(parts) < 2:
        print("Usage: /resource <name>")
        return

    resource_id = parts[1]

    try:
        # Get all available resources
        response = await session.list_resources()
        resources = response.resources
        resource_map = {str(i + 1): r.name for i, r in enumerate(resources)}

        # Resolve name or index
        resource_name = resource_map.get(resource_id, resource_id)
        match = next((r for r in resources if r.name == resource_name), None)

        if not match:
            print(f"Resource '{resource_id}' not found.")
            return

        # Fetch resource content
        result = await session.read_resource(match.uri)

        for content in result.contents:
            if hasattr(content, "text"):
                print("\n=== Resource Text ===")
                print(content.text)

    except Exception as e:
        print("Resource fetch failed:", e)

async def list_prompts(session):
    prompt_response = await session.list_prompts()

    if not prompt_response or not prompt_response.prompts:
        print("No prompts found on the server.")
        return

    print("\nAvailable Prompts and Argument Structure:")
    for p in prompt_response.prompts:
        print(f"\nPrompt: {p.name}")
        if p.arguments:
            for arg in p.arguments:
                print(f"  - {arg.name}")
        else:
            print("  - No arguments required.")
    print("\nUse: /prompt <prompt_name> \"arg1\" \"arg2\" ...")

async def handle_prompt(session, tools, command, agent):
    parts = shlex.split(command.strip())
    if len(parts) < 2:
        print("Usage: /prompt <name> \"args>\"")
        return

    prompt_name = parts[1]
    args = parts[2:]

    try:
        # Get available prompts
        prompt_def = await session.list_prompts()
        match = next((p for p in prompt_def.prompts if p.name == prompt_name), None)
        if not match:
            print(f"Prompt '{prompt_name}' not found.")
            return

        # Check arg count
        if len(args) != len(match.arguments):
            expected = ", ".join([a.name for a in match.arguments])
            print(f"Expected {len(match.arguments)} arguments: {expected}")
            return

        # Build argument dict
        arg_values = {arg.name: val for arg, val in zip(match.arguments, args)}
        response = await session.get_prompt(prompt_name, arg_values)
        prompt_text = response.messages[0].content.text
        
        # Execute the prompt via the agent
        agent_response = await agent.ainvoke(
            {"messages": [HumanMessage(content=prompt_text)]},
            config={"configurable": {"thread_id": "wiki-session"}}
        )
        print("\n=== Prompt Result ===")
        print(agent_response["messages"][-1].content)

    except Exception as e:
        print("Prompt invocation failed:", e)


# Entry point
async def main():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            tools = await load_mcp_tools(session)
            agent = await create_graph(session)

            print("Wikipedia MCP agent is ready.")
            print("Type a question or use the following templates:")
            print("  /prompts                - to list available prompts")
            print("  /prompt <name> \"args\"   - to run a specific prompt")
            print("  /resources              - to list available resources")
            print("  /resource <name>        - to run a specific resource")

            while True:
                user_input = input("\nYou: ").strip()
                if user_input.lower() in {"exit", "quit", "q"}:
                    break
                elif user_input.startswith("/prompts"):
                    await list_prompts(session)
                    continue
                elif user_input.startswith("/prompt"):
                    await handle_prompt(session, tools, user_input, agent)
                    continue
                elif user_input.startswith("/resources"):
                    await list_resources(session)
                    continue
                elif user_input.startswith("/resource"):
                    await handle_resource(session, user_input)
                    continue

                try:
                    response = await agent.ainvoke(
                        {"messages": user_input},
                        config={"configurable": {"thread_id": "wiki-session"}}
                    )
                    print("AI:", response["messages"][-1].content)
                except Exception as e:
                    print("Error:", e)


if __name__ == "__main__":
    asyncio.run(main())