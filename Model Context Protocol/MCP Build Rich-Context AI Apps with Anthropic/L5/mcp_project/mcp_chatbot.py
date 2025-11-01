from dotenv import load_dotenv
from openai import OpenAI 
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from typing import List
import asyncio
import nest_asyncio
import json

nest_asyncio.apply()

load_dotenv()

class MCP_ChatBot:

    def __init__(self):
        # Initialize session and client objects
        self.session: ClientSession = None
        self.openAI = OpenAI()
        self.available_tools: List[dict] = []

    async def process_query(self, query):
        # Initialize the conversation with the user query
        messages = [{'role': 'user', 'content': query}]

        # Make the initial API call to OpenAI
        response = self.openAI.chat.completions.create(
            max_tokens=2024,
            model='gpt-4o',  # or other models like 'gpt-4-turbo', 'gpt-3.5-turbo'
            tools=self.available_tools,  # Assumes 'tools' is defined in the outer scope
            tool_choice='auto',  # Let the model decide whether to use tools
            messages=messages
        )

        process_query = True
        while process_query:
            # Get the assistant's message from the response
            assistant_message = response.choices[0].message

            # Check if the assistant is using tools or providing a text response
            if assistant_message.tool_calls:
                # Assistant wants to use tools

                # If there's any text content alongside the tool calls, print it
                if assistant_message.content:
                    print(assistant_message.content)

                # Add the assistant's message to conversation history
                messages.append({
                    'role': 'assistant',
                    'content': assistant_message.content,
                    'tool_calls': assistant_message.tool_calls
                })

                # Process each tool call
                for tool_call in assistant_message.tool_calls:
                    tool_id = tool_call.id
                    tool_name = tool_call.function.name
                    # OpenAI provides arguments as a JSON string, so we need to parse it
                    tool_args = json.loads(tool_call.function.arguments)

                    print(f"Calling tool {tool_name} with args {tool_args}")

                    # Execute the tool (assumes execute_tool function is defined elsewhere)
                    result = await self.session.call_tool(tool_name, arguments=tool_args)

                    # Add the tool result to the conversation
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_id,
                        "content": str(result.content[0].text) if result.content else str(result)
                    })

                # Make another API call with the updated conversation including tool results
                response = self.openAI.chat.completions.create(
                    max_tokens=2024,
                    model='gpt-4o',
                    tools=self.available_tools,
                    tool_choice='auto',
                    messages=messages
                )

                # Check if this response has only text content (no more tool calls)
                if not response.choices[0].message.tool_calls:
                    print(response.choices[0].message.content)
                    process_query = False

            else:
                # Assistant provided a text response (no tool calls)
                if assistant_message.content:
                    print(assistant_message.content)
                process_query = False



    async def chat_loop(self):
        """Run an interactive chat loop"""
        print("\nMCP Chatbot Started!")
        print("Type your queries or 'quit' to exit.")

        while True:
            try:
                query = input("\nQuery: ").strip()

                if query.lower() == 'quit':
                    break

                await self.process_query(query)
                print("\n")

            except Exception as e:
                print(f"\nError: {str(e)}")

    async def connect_to_server_and_run(self):
        # Create server parameters for stdio connection
        server_params = StdioServerParameters(
            command="uv",  # Executable
            args=["run", "research_server.py"],  # Optional command line arguments
            env=None,  # Optional environment variables
        )
        async with stdio_client(server_params) as (read, write):
            async with ClientSession(read, write) as session:
                self.session = session
                # Initialize the connection
                await session.initialize()

                # List available tools
                response = await session.list_tools()

                tools = response.tools
                print("\nConnected to server with tools:", [tool.name for tool in tools])

                self.available_tools = [{
                    "type": "function",
                    "function": {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.inputSchema
                    }
                } for tool in response.tools]

                await self.chat_loop()


async def main():
    chatbot = MCP_ChatBot()
    await chatbot.connect_to_server_and_run()


if __name__ == "__main__":
    asyncio.run(main())
