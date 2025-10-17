import { ChatOpenAI } from '@langchain/openai';
import { LangChainAdapter } from 'ai';
import { StateGraph, START, END } from 'langgraph';
import { HumanMessage } from 'langchain/schema';
import { NextRequest, NextResponse } from 'next/server';

// Define the AI agent's state structure
type AgentState = {
  query: string;
  response: string;
};

// Initialize the LangChain model with streaming enabled
const model = new ChatOpenAI({
  model: 'gpt-3.5-turbo-0125',
  temperature: 0,
  streaming: true,
});

// Define the node function for processing user queries
async function handleQuery(state: AgentState): Promise<AgentState> {
  const userMessage = new HumanMessage(state.query);
  const aiResponse = await model.invoke([userMessage]);
  return { ...state, response: aiResponse.content };
}

// Build the LangGraph workflow for the AI agent
const builder = new StateGraph<AgentState>();
builder.addNode("handleQuery", handleQuery);
builder.addEdge(START, "handleQuery");
builder.addEdge("handleQuery", END);
const graph = builder.compile();

// Define the Next.js API route for streaming responses
export async function POST(req: NextRequest) {
  const { prompt } = await req.json();

  // Initialize the agent's initial state
  const initialState = { query: prompt, response: '' };

  // Use LangGraph's asynchronous streaming to process the workflow
  const stream = await graph.astream(initialState, { stream_mode: "messages" });

  // Convert the LangGraph stream to a Next.js AI SDK-compatible stream
  return LangChainAdapter.toDataStreamResponse(stream);
}
