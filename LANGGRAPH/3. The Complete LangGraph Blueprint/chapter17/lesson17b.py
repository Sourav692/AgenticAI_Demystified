from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit
from typing import TypedDict
from langgraph.graph import StateGraph, START, END
from langchain_openai import ChatOpenAI
from langchain.schema import HumanMessage
import eventlet

# Define the agent's state
class AgentState(TypedDict):
    query: str
    response: str

# Initialize the AI tool (e.g., OpenAI API)
llm_tool = ChatOpenAI(temperature=0, model_name="gpt-4o-mini")

# Define the node that processes user queries
def handle_query(state: AgentState) -> AgentState:
    user_message = HumanMessage(content=state['query'])
    ai_response = llm_tool.invoke([user_message])
    state['response'] = ai_response.content
    return state

# Build the LangGraph workflow for the agent
builder = StateGraph(AgentState)
builder.add_node("handle_query", handle_query)
builder.add_edge(START, "handle_query")
builder.add_edge("handle_query", END)
graph = builder.compile()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'

# Allow CORS only from http://localhost:3000
CORS(app, resources={r"/*": {"origins": "http://localhost:3000"}})

# Initialize SocketIO with CORS settings for SocketIO
socketio = SocketIO(
    app,
    async_mode='eventlet',
    cors_allowed_origins=["http://localhost:3000"],
    logger=True,
    engineio_logger=True
)

# Define the REST endpoint for non-streaming queries
@app.route('/api/agent', methods=['POST'])
def agent():
    data = request.json
    query = data.get("query", "")
    initial_state = {"query": query, "response": ""}
    result = graph.invoke(initial_state)
    return jsonify({"response": result['response']})

# Define a WebSocket event for streaming responses
@socketio.on('connect')
def handle_connect():
    print("Client connected")  # Debugging log

@socketio.on('disconnect')
def handle_disconnect():
    print("Client disconnected")  # Debugging log

@socketio.on('stream_query')
async def handle_stream_query(data):
    try:
        query = data.get("query", "")
        initial_state = {"query": query, "response": ""}
        print(f"Received query: {query}")  # Debugging log

        # Stream responses using LangGraph's async stream with stream_mode="values"
        async for chunk in graph.astream(initial_state, stream_mode="values"):
            print(f"Emitting chunk: {chunk['response']}")  # Debugging log
            emit('response_chunk', {'chunk': chunk['response']})  # Stream each chunk to the client

        emit('response_complete', {'message': 'Response streaming complete'})
        print("Streaming complete")  # Debugging log

    except Exception as e:
        print(f"Error in handle_stream_query: {str(e)}")
        emit('error', {'message': str(e)})

# Start the application with SocketIO
if __name__ == '__main__':
    socketio.run(app, debug=True, host='0.0.0.0', port=5000)
