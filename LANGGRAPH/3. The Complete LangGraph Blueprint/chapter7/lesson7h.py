from langgraph.graph import StateGraph, MessagesState, START, END
from langchain_openai import ChatOpenAI
from langchain.callbacks.streaming_stdout import StreamingStdOutCallbackHandler

# First example with streaming enabled
llm_streaming = ChatOpenAI(
    model="gpt-4o-mini", 
    temperature=1,
    streaming=True,
    callbacks=[StreamingStdOutCallbackHandler()]
)

# Second example with streaming disabled
llm_no_streaming = ChatOpenAI(
    model="gpt-4o-mini", 
    temperature=1,
    streaming=False
)

def create_graph(llm):
    graph_builder = StateGraph(MessagesState)
    
    def chatbot(state: MessagesState):
        messages = state["messages"]
        if not isinstance(messages, list):
            messages = [messages]
        return {"messages": llm.invoke(messages)}

    graph_builder.add_node("chatbot", chatbot)
    graph_builder.add_edge(START, "chatbot")
    graph_builder.add_edge("chatbot", END)
    return graph_builder.compile()

input = {
    "messages": [
        {
            "role": "user", 
            "content": "how many r's are in strawberry? Explain in three paragraphs."
        }
    ]
}

print("With streaming enabled:")
graph_streaming = create_graph(llm_streaming)
for output in graph_streaming.stream(input):
    if isinstance(output, dict) and 'chatbot' in output:
        # We don't need to print here as StreamingStdOutCallbackHandler handles it
        pass

print("\n\nWith streaming disabled:")
graph_no_streaming = create_graph(llm_no_streaming)
for output in graph_no_streaming.stream(input):
    if isinstance(output, dict) and 'chatbot' in output:
        message = output['chatbot']['messages']
        print(message.content, end="", flush=True)