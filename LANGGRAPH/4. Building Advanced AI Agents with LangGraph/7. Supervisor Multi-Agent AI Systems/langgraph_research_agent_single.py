"""
LangGraph Research & Summarization Agent - Single File Implementation

A sophisticated multi-agent system that intelligently routes queries to specialized agents:
- Router Agent: Determines the best processing path
- Web Search Agent: Retrieves current information from the web
- RAG Agent: Retrieves from vector database knowledge base
- LLM Agent: Handles direct reasoning and analysis
- Summarization Agent: Synthesizes final structured responses

Requirements:
    pip install langgraph langchain langchain-openai langchain-community langchain-chroma chromadb tavily-python python-dotenv tiktoken

Usage:
    # Interactive mode
    python langgraph_research_agent_single.py

    # Single query mode
    python langgraph_research_agent_single.py "What is machine learning?"

    # Set API keys as environment variables or in code below
"""

import os
import sys
from typing import TypedDict, Annotated, List, Optional, Literal, Dict
from dotenv import load_dotenv
import operator

# LangChain imports
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import BaseMessage
from langchain_core.pydantic_v1 import BaseModel, Field
from langchain.schema import Document
from langchain_community.tools.tavily_search import TavilySearchResults

# LangGraph imports
from langgraph.graph import StateGraph, END

# Load environment variables
load_dotenv()


# ============================================================================
# CONFIGURATION
# ============================================================================

class Config:
    """Configuration for the agent system"""
    
    # API Keys - SET THESE OR USE .env FILE
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "your-openai-key-here")
    TAVILY_API_KEY = os.getenv("TAVILY_API_KEY", "your-tavily-key-here")
    
    # Model Configuration
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o")
    OPENAI_TEMPERATURE = float(os.getenv("OPENAI_TEMPERATURE", "0.7"))
    
    # RAG Configuration
    CHROMA_PERSIST_DIRECTORY = "./chroma_db_single"
    COLLECTION_NAME = "knowledge_base"
    EMBEDDING_MODEL = "text-embedding-3-small"
    
    # Search Configuration
    MAX_SEARCH_RESULTS = 5
    
    @classmethod
    def validate(cls):
        """Validate that required configuration is present"""
        if not cls.OPENAI_API_KEY or cls.OPENAI_API_KEY == "your-openai-key-here":
            raise ValueError(
                "OPENAI_API_KEY not set. Please set it in the code or as environment variable."
            )
        if not cls.TAVILY_API_KEY or cls.TAVILY_API_KEY == "your-tavily-key-here":
            raise ValueError(
                "TAVILY_API_KEY not set. Please set it in the code or as environment variable."
            )
        return True


# ============================================================================
# STATE DEFINITION
# ============================================================================

class AgentState(TypedDict):
    """
    State object that flows through the graph nodes.
    
    Attributes:
        query: The original user query
        messages: List of messages in the conversation
        route_decision: Decision made by router ('llm', 'web_search', 'rag')
        web_search_results: Results from web search agent
        rag_results: Results from RAG agent
        llm_response: Direct response from LLM
        final_response: Final summarized response
        metadata: Additional metadata for tracking
    """
    query: str
    messages: Annotated[List[BaseMessage], operator.add]
    route_decision: Optional[str]
    web_search_results: Optional[str]
    rag_results: Optional[str]
    llm_response: Optional[str]
    final_response: Optional[str]
    metadata: Optional[dict]


# ============================================================================
# ROUTER AGENT
# ============================================================================

class RouteDecision(BaseModel):
    """Decision model for routing"""
    route: Literal["llm", "web_search", "rag"] = Field(
        description="The route to take: 'llm' for direct reasoning, 'web_search' for current information, 'rag' for knowledge base retrieval"
    )
    reasoning: str = Field(
        description="Brief explanation of why this route was chosen"
    )


class RouterAgent:
    """
    Router Agent that analyzes queries and determines the best processing path.
    
    Routing Logic:
    - web_search: For queries containing temporal keywords (latest, current, today, recent, now, 2024, 2025, etc.)
    - rag: For queries about predefined knowledge (technical concepts, historical facts, domain knowledge)
    - llm: For general reasoning, analysis, creative tasks that don't require external data
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            temperature=0.1,  # Lower temperature for more consistent routing
            api_key=Config.OPENAI_API_KEY
        ).with_structured_output(RouteDecision)
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a routing agent that determines how to process user queries.

Analyze the query and decide which agent should handle it:

1. **web_search** - Choose this route if:
   - Query contains temporal indicators: "latest", "current", "today", "recent", "now", "this year", dates like "2024", "2025"
   - Query asks about real-time information: news, weather, stock prices, sports scores
   - Query requires up-to-date information that changes frequently

2. **rag** - Choose this route if:
   - Query is about technical concepts, theories, or established knowledge
   - Query asks about information likely in a knowledge base (e.g., "What is machine learning?")
   - Query is about historical facts, definitions, or domain-specific knowledge
   - Query does NOT require current/latest information

3. **llm** - Choose this route if:
   - Query requires reasoning, analysis, or creative thinking
   - Query is conversational or asks for opinions
   - Query involves calculations, problem-solving, or explanations
   - Query doesn't require external information sources

Important: Prioritize web_search for any query with temporal indicators, even if it could also be answered by RAG or LLM."""),
            ("human", "Query: {query}\n\nDetermine the best route and explain your reasoning.")
        ])
    
    def route(self, state: dict) -> dict:
        """Analyze the query and determine routing decision"""
        query = state["query"]
        
        # Invoke the LLM with structured output
        chain = self.prompt | self.llm
        decision = chain.invoke({"query": query})
        
        print(f"\n🔀 Router Decision: {decision.route}")
        print(f"📝 Reasoning: {decision.reasoning}\n")
        
        return {
            "route_decision": decision.route,
            "metadata": {
                "routing_reasoning": decision.reasoning
            }
        }


# ============================================================================
# WEB SEARCH AGENT
# ============================================================================

class WebSearchAgent:
    """
    Web Search Agent that retrieves current information from the web.
    Uses Tavily API for high-quality search results.
    """
    
    def __init__(self):
        self.search_tool = TavilySearchResults(
            max_results=Config.MAX_SEARCH_RESULTS,
            api_key=Config.TAVILY_API_KEY,
            search_depth="advanced",
            include_answer=True,
            include_raw_content=False
        )
        
        self.llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            temperature=Config.OPENAI_TEMPERATURE,
            api_key=Config.OPENAI_API_KEY
        )
        
        self.extraction_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a web research analyst. Your task is to extract and synthesize relevant information from web search results.

Given a query and search results, extract the most relevant information that answers the query.

Format your response as a well-structured summary with:
- Key findings
- Important details
- Source citations

Be concise but comprehensive."""),
            ("human", """Query: {query}

Search Results:
{search_results}

Extract and synthesize the relevant information:""")
        ])
    
    def search(self, state: dict) -> dict:
        """Perform web search and extract relevant information"""
        query = state["query"]
        
        print(f"🌐 Performing web search for: '{query}'")
        
        try:
            # Perform search
            search_results = self.search_tool.invoke({"query": query})
            
            # Format search results for LLM processing
            formatted_results = self._format_search_results(search_results)
            
            # Extract and synthesize information using LLM
            chain = self.extraction_prompt | self.llm
            extracted_info = chain.invoke({
                "query": query,
                "search_results": formatted_results
            })
            
            result_text = extracted_info.content
            
            print(f"✅ Web search completed. Found {len(search_results)} results\n")
            
            return {
                "web_search_results": result_text
            }
            
        except Exception as e:
            error_msg = f"Error during web search: {str(e)}"
            print(f"❌ {error_msg}\n")
            return {
                "web_search_results": f"Unable to retrieve web search results: {error_msg}"
            }
    
    def _format_search_results(self, results: List[Dict]) -> str:
        """Format search results into a readable string"""
        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(f"Result {i}:")
            formatted.append(f"Title: {result.get('title', 'N/A')}")
            formatted.append(f"Content: {result.get('content', 'N/A')}")
            formatted.append(f"URL: {result.get('url', 'N/A')}")
            formatted.append("---")
        
        return "\n".join(formatted)


# ============================================================================
# RAG AGENT
# ============================================================================

class RAGAgent:
    """
    RAG (Retrieval-Augmented Generation) Agent that retrieves information
    from a vector database and generates responses.
    """
    
    def __init__(self):
        self.embeddings = OpenAIEmbeddings(
            model=Config.EMBEDDING_MODEL,
            api_key=Config.OPENAI_API_KEY
        )
        
        self.llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            temperature=Config.OPENAI_TEMPERATURE,
            api_key=Config.OPENAI_API_KEY
        )
        
        # Initialize or load vector store
        self.vector_store = self._initialize_vector_store()
        
        self.rag_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a knowledgeable assistant. Use the provided context from the knowledge base to answer the query.

If the context contains relevant information, provide a comprehensive answer based on it.
If the context doesn't contain enough information, acknowledge this and provide what you can.

Always cite which parts of the context you used."""),
            ("human", """Query: {query}

Context from Knowledge Base:
{context}

Provide a detailed answer based on the context:""")
        ])
    
    def _initialize_vector_store(self) -> Chroma:
        """Initialize or create the vector store"""
        
        # Check if vector store exists
        if os.path.exists(Config.CHROMA_PERSIST_DIRECTORY):
            print("📚 Loading existing vector store...")
            vector_store = Chroma(
                collection_name=Config.COLLECTION_NAME,
                embedding_function=self.embeddings,
                persist_directory=Config.CHROMA_PERSIST_DIRECTORY
            )
        else:
            print("📚 Creating new vector store with sample data...")
            # Create sample knowledge base
            sample_documents = self._create_sample_documents()
            
            vector_store = Chroma.from_documents(
                documents=sample_documents,
                embedding=self.embeddings,
                collection_name=Config.COLLECTION_NAME,
                persist_directory=Config.CHROMA_PERSIST_DIRECTORY
            )
        
        return vector_store
    
    def _create_sample_documents(self) -> List[Document]:
        """Create sample documents for the knowledge base"""
        
        documents = [
            Document(
                page_content="Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed. It focuses on developing computer programs that can access data and use it to learn for themselves.",
                metadata={"source": "ml_basics", "topic": "machine_learning"}
            ),
            Document(
                page_content="Deep learning is a subset of machine learning that uses neural networks with multiple layers. These neural networks attempt to simulate the behavior of the human brain, allowing it to learn from large amounts of data.",
                metadata={"source": "dl_basics", "topic": "deep_learning"}
            ),
            Document(
                page_content="Natural Language Processing (NLP) is a branch of artificial intelligence that helps computers understand, interpret, and manipulate human language. NLP draws from many disciplines, including computer science and computational linguistics.",
                metadata={"source": "nlp_basics", "topic": "nlp"}
            ),
            Document(
                page_content="Apache Spark is a unified analytics engine for large-scale data processing. It provides high-level APIs in Java, Scala, Python, and R, and an optimized engine that supports general execution graphs.",
                metadata={"source": "spark_basics", "topic": "big_data"}
            ),
            Document(
                page_content="Databricks is a unified data analytics platform built on Apache Spark. It provides collaborative notebooks, optimized Spark clusters, and production-grade workflows for data engineering, data science, and machine learning.",
                metadata={"source": "databricks_basics", "topic": "data_platform"}
            ),
            Document(
                page_content="Data lakehouse is a data management architecture that combines the best features of data lakes and data warehouses. It provides the flexibility and scalability of data lakes with the data management and ACID transactions of data warehouses.",
                metadata={"source": "lakehouse_basics", "topic": "data_architecture"}
            ),
            Document(
                page_content="ETL (Extract, Transform, Load) is a data integration process that involves extracting data from various sources, transforming it into a suitable format, and loading it into a target database or data warehouse.",
                metadata={"source": "etl_basics", "topic": "data_engineering"}
            ),
            Document(
                page_content="Feature engineering is the process of selecting, manipulating, and transforming raw data into features that can be used in supervised learning. It is a crucial step in machine learning that can significantly impact model performance.",
                metadata={"source": "feature_eng", "topic": "machine_learning"}
            ),
            Document(
                page_content="A neural network is a series of algorithms that endeavors to recognize underlying relationships in a set of data through a process that mimics the way the human brain operates. It consists of layers of interconnected nodes (neurons).",
                metadata={"source": "neural_net", "topic": "deep_learning"}
            ),
            Document(
                page_content="Cloud computing is the delivery of computing services including servers, storage, databases, networking, software, analytics, and intelligence over the Internet to offer faster innovation, flexible resources, and economies of scale.",
                metadata={"source": "cloud_basics", "topic": "cloud_computing"}
            ),
            Document(
                page_content="LangChain is a framework for developing applications powered by language models. It enables applications that are context-aware and can reason based on provided context and instructions.",
                metadata={"source": "langchain_basics", "topic": "frameworks"}
            ),
            Document(
                page_content="Vector databases are specialized databases designed to store and query high-dimensional vectors efficiently. They are essential for semantic search, recommendation systems, and RAG applications.",
                metadata={"source": "vector_db", "topic": "databases"}
            )
        ]
        
        return documents
    
    def retrieve(self, state: dict) -> dict:
        """Retrieve relevant information from knowledge base and generate response"""
        query = state["query"]
        
        print(f"📖 Retrieving from knowledge base for: '{query}'")
        
        try:
            # Retrieve relevant documents
            retriever = self.vector_store.as_retriever(
                search_type="similarity",
                search_kwargs={"k": 4}
            )
            
            relevant_docs = retriever.invoke(query)
            
            # Format context from retrieved documents
            context = self._format_documents(relevant_docs)
            
            # Generate response using retrieved context
            chain = self.rag_prompt | self.llm
            response = chain.invoke({
                "query": query,
                "context": context
            })
            
            result_text = response.content
            
            print(f"✅ RAG retrieval completed. Found {len(relevant_docs)} relevant documents\n")
            
            return {
                "rag_results": result_text
            }
            
        except Exception as e:
            error_msg = f"Error during RAG retrieval: {str(e)}"
            print(f"❌ {error_msg}\n")
            return {
                "rag_results": f"Unable to retrieve from knowledge base: {error_msg}"
            }
    
    def _format_documents(self, docs: List[Document]) -> str:
        """Format retrieved documents into a readable context string"""
        formatted = []
        for i, doc in enumerate(docs, 1):
            formatted.append(f"Document {i}:")
            formatted.append(f"Content: {doc.page_content}")
            formatted.append(f"Source: {doc.metadata.get('source', 'unknown')}")
            formatted.append("---")
        
        return "\n".join(formatted)


# ============================================================================
# LLM AGENT
# ============================================================================

class LLMAgent:
    """
    LLM Agent that handles queries requiring direct reasoning, analysis,
    or creative thinking without external information sources.
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            temperature=Config.OPENAI_TEMPERATURE,
            api_key=Config.OPENAI_API_KEY
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a helpful AI assistant with strong reasoning and analytical capabilities.

Provide thoughtful, well-structured responses to queries that require:
- Logical reasoning and analysis
- Creative thinking and ideation
- Problem-solving and explanations
- Conversational responses

Be clear, concise, and comprehensive in your responses."""),
            ("human", "{query}")
        ])
    
    def respond(self, state: dict) -> dict:
        """Generate direct response using LLM reasoning"""
        query = state["query"]
        
        print(f"🤖 Generating LLM response for: '{query}'")
        
        try:
            chain = self.prompt | self.llm
            response = chain.invoke({"query": query})
            
            result_text = response.content
            
            print(f"✅ LLM response generated\n")
            
            return {
                "llm_response": result_text
            }
            
        except Exception as e:
            error_msg = f"Error during LLM processing: {str(e)}"
            print(f"❌ {error_msg}\n")
            return {
                "llm_response": f"Unable to generate response: {error_msg}"
            }


# ============================================================================
# SUMMARIZATION AGENT
# ============================================================================

class SummarizationAgent:
    """
    Summarization Agent that synthesizes information from various sources
    into a final, well-structured response.
    """
    
    def __init__(self):
        self.llm = ChatOpenAI(
            model=Config.OPENAI_MODEL,
            temperature=Config.OPENAI_TEMPERATURE,
            api_key=Config.OPENAI_API_KEY
        )
        
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", """You are an expert at synthesizing information into clear, well-structured responses.

Your task is to create a final response that:
1. Directly answers the user's query
2. Integrates all relevant information provided
3. Is well-organized with clear structure (use headings, bullet points, etc.)
4. Maintains accuracy and cites sources when applicable
5. Is concise yet comprehensive

Format the response for maximum clarity and readability."""),
            ("human", """Original Query: {query}

Route Used: {route}

Information Gathered:
{content}

Create a final, well-structured response that synthesizes this information:""")
        ])
    
    def summarize(self, state: dict) -> dict:
        """Synthesize final response from gathered information"""
        query = state["query"]
        route = state.get("route_decision", "unknown")
        
        # Gather content from appropriate source
        content = self._get_content(state, route)
        
        print(f"📝 Synthesizing final response...")
        
        try:
            chain = self.prompt | self.llm
            response = chain.invoke({
                "query": query,
                "route": route,
                "content": content
            })
            
            result_text = response.content
            
            print(f"✅ Final response generated\n")
            
            return {
                "final_response": result_text
            }
            
        except Exception as e:
            error_msg = f"Error during summarization: {str(e)}"
            print(f"❌ {error_msg}\n")
            return {
                "final_response": f"Unable to generate summary: {error_msg}"
            }
    
    def _get_content(self, state: dict, route: str) -> str:
        """Extract content based on the route taken"""
        
        if route == "web_search":
            return state.get("web_search_results", "No web search results available")
        elif route == "rag":
            return state.get("rag_results", "No RAG results available")
        elif route == "llm":
            return state.get("llm_response", "No LLM response available")
        else:
            return "No content available"


# ============================================================================
# LANGGRAPH WORKFLOW
# ============================================================================

class ResearchGraph:
    """
    Main graph orchestrating the research and summarization workflow
    """
    
    def __init__(self):
        # Initialize all agents
        self.router_agent = RouterAgent()
        self.web_search_agent = WebSearchAgent()
        self.rag_agent = RAGAgent()
        self.llm_agent = LLMAgent()
        self.summarization_agent = SummarizationAgent()
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """
        Build the state graph with nodes and conditional edges
        
        Graph Flow:
        1. Start -> Router (determines path)
        2. Router -> [Web Search | RAG | LLM] (conditional based on route)
        3. [Web Search | RAG | LLM] -> Summarizer
        4. Summarizer -> End
        """
        
        # Create state graph
        workflow = StateGraph(AgentState)
        
        # Add nodes
        workflow.add_node("router", self.router_agent.route)
        workflow.add_node("web_search", self.web_search_agent.search)
        workflow.add_node("rag", self.rag_agent.retrieve)
        workflow.add_node("llm", self.llm_agent.respond)
        workflow.add_node("summarizer", self.summarization_agent.summarize)
        
        # Set entry point
        workflow.set_entry_point("router")
        
        # Add conditional edges from router
        workflow.add_conditional_edges(
            "router",
            self._route_decision,
            {
                "web_search": "web_search",
                "rag": "rag",
                "llm": "llm"
            }
        )
        
        # Add edges from processing nodes to summarizer
        workflow.add_edge("web_search", "summarizer")
        workflow.add_edge("rag", "summarizer")
        workflow.add_edge("llm", "summarizer")
        
        # Add edge from summarizer to end
        workflow.add_edge("summarizer", END)
        
        # Compile the graph
        return workflow.compile()
    
    def _route_decision(self, state: AgentState) -> str:
        """Decision function for conditional routing"""
        return state["route_decision"]
    
    def invoke(self, query: str) -> dict:
        """Execute the graph with a query"""
        
        # Initialize state
        initial_state = {
            "query": query,
            "messages": [],
            "route_decision": None,
            "web_search_results": None,
            "rag_results": None,
            "llm_response": None,
            "final_response": None,
            "metadata": {}
        }
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        return final_state


# ============================================================================
# MAIN APPLICATION
# ============================================================================

def print_banner():
    """Print welcome banner"""
    print("=" * 80)
    print("🤖 LangGraph Research & Summarization Agent")
    print("=" * 80)
    print("\nThis agent can:")
    print("  • Answer queries with direct reasoning (LLM)")
    print("  • Search the web for current information (Web Search)")
    print("  • Retrieve from knowledge base (RAG)")
    print("\nType 'exit' or 'quit' to end the session")
    print("Type 'help' for example queries\n")
    print("=" * 80)


def print_help():
    """Print example queries"""
    print("\n" + "=" * 80)
    print("📚 EXAMPLE QUERIES")
    print("=" * 80)
    print("\n🔍 Web Search (Current Information):")
    print("  • What are the latest AI developments in 2025?")
    print("  • Current weather in New York")
    print("  • Recent news about technology")
    print("\n📖 RAG (Knowledge Base):")
    print("  • What is machine learning?")
    print("  • Explain Databricks")
    print("  • Define deep learning")
    print("\n🤖 LLM (Direct Reasoning):")
    print("  • Compare supervised vs unsupervised learning")
    print("  • Explain the benefits of microservices")
    print("  • How to design a scalable system")
    print("=" * 80 + "\n")


def print_result(final_state: dict):
    """Print the final result in a formatted way"""
    print("\n" + "=" * 80)
    print("📊 RESULTS")
    print("=" * 80)
    
    print(f"\n📍 Query: {final_state['query']}")
    print(f"🔀 Route: {final_state['route_decision']}")
    
    if final_state.get('metadata', {}).get('routing_reasoning'):
        print(f"💭 Routing Reasoning: {final_state['metadata']['routing_reasoning']}")
    
    print("\n" + "-" * 80)
    print("📝 FINAL RESPONSE")
    print("-" * 80)
    print(f"\n{final_state['final_response']}\n")
    print("=" * 80 + "\n")


def interactive_mode(graph: ResearchGraph):
    """Run in interactive mode"""
    print_banner()
    
    while True:
        try:
            query = input("🔍 Enter your query (or 'help' for examples): ").strip()
            
            if not query:
                continue
            
            if query.lower() in ['exit', 'quit']:
                print("\n👋 Goodbye!\n")
                break
            
            if query.lower() == 'help':
                print_help()
                continue
            
            print("\n🚀 Processing query...\n")
            
            # Execute the graph
            final_state = graph.invoke(query)
            
            # Print results
            print_result(final_state)
            
        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {str(e)}\n")


def single_query_mode(graph: ResearchGraph, query: str):
    """Run with a single query"""
    print_banner()
    print(f"\n🚀 Processing query: {query}\n")
    
    try:
        # Execute the graph
        final_state = graph.invoke(query)
        
        # Print results
        print_result(final_state)
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}\n")


def main():
    """Main function"""
    try:
        # Validate configuration
        Config.validate()
        
        # Initialize the graph
        print("\n🔧 Initializing Research Agent...\n")
        graph = ResearchGraph()
        print("✅ Agent initialized successfully!\n")
        
        # Check for command line arguments
        if len(sys.argv) > 1:
            # Single query mode
            query = " ".join(sys.argv[1:])
            single_query_mode(graph, query)
        else:
            # Interactive mode
            interactive_mode(graph)
            
    except ValueError as e:
        print(f"\n❌ Configuration Error: {str(e)}")
        print("\nPlease set your API keys:")
        print("1. Edit the Config class in this file, OR")
        print("2. Set environment variables:")
        print("   export OPENAI_API_KEY='your-key-here'")
        print("   export TAVILY_API_KEY='your-key-here'")
        print("\nGet API keys from:")
        print("  • OpenAI: https://platform.openai.com")
        print("  • Tavily: https://tavily.com\n")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected Error: {str(e)}\n")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
