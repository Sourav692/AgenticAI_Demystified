import { ChatOpenAI } from '@langchain/openai';
import { LangChainAdapter } from 'ai';

export const maxDuration = 60;

export async function POST(req: Request) {
  // Extract the prompt text from the incoming request body
  const { prompt } = await req.json();

  // Initialize the LangChain model (OpenAI in this case)
  const model = new ChatOpenAI({
    model: 'gpt-4o-mini', // Model version can be updated
    temperature: 0,              // Temperature controls response randomness
  });

  // Use the model's stream method to enable streaming responses
  const stream = await model.stream(prompt);

  // Convert the LangChain response stream into a Data Stream compatible with Next.js AI SDK
  return LangChainAdapter.toDataStreamResponse(stream);
}
