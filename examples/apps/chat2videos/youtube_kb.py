from os import getenv

from agno.agent import Agent
from agno.knowledge.youtube import YouTubeKnowledgeBase, YouTubeReader
from agno.models.ollama import Ollama
from agno.embedder.ollama import OllamaEmbedder
from agno.vectordb.pgvector import PgVector
model=Ollama(id="llama3.2:latest")
embedder=OllamaEmbedder(id="nomic-embed-text:latest", dimensions=768)


db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

vector_db = PgVector(table_name="youtube-db-01", 
                     db_url=db_url,
                     embedder=embedder)
# Create a knowledge base with the PDFs from the data/pdfs directory
knowledge_base = YouTubeKnowledgeBase(
    urls=["https://www.youtube.com/watch?v=CDC3GOuJyZ0"],
    vector_db=vector_db,
    reader=YouTubeReader(chunk=True),
)
# knowledge_base.load(recreate=False)  # only once, comment it out after first run

agent = Agent(
    model=model,
    knowledge=knowledge_base,
    search_knowledge=True,
)

agent.print_response(
    "What is the major focus of the knowledge provided?", markdown=True
)
