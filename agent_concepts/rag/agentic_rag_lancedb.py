"""
1. Run: `pip install openai lancedb tantivy pypdf sqlalchemy agno` to install the dependencies
2. Run: `python cookbook/rag/04_agentic_rag_lancedb.py` to run the agent
"""

from agno.agent import Agent
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.models.ollama import Ollama
from agno.embedder.ollama import OllamaEmbedder

model=Ollama(id="llama3.2:latest")
embedder=OllamaEmbedder(id="llama3.2:latest", dimensions=3072) 
# Create a knowledge base of PDFs from URLs
knowledge_base = PDFUrlKnowledgeBase(
    urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
    # Use LanceDB as the vector database and store embeddings in the `recipes` table
    vector_db=LanceDb(
        table_name="recipes3",
        uri="tmp/lancedb",
        search_type=SearchType.vector,
        embedder=embedder,
    ),
)
# Load the knowledge base: Comment after first run as the knowledge base is already loaded
knowledge_base.load()

agent = Agent(
    model=model,
    knowledge=knowledge_base,
    # Add a tool to search the knowledge base which enables agentic RAG.
    # This is enabled by default when `knowledge` is provided to the Agent.
    search_knowledge=True,
    show_tool_calls=True,
    markdown=True,
)
agent.print_response(
    "How do I make chicken and galangal in coconut milk soup", stream=True
)
