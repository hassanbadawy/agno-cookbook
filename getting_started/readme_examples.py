"""Readme Examples
Run `pip install openai duckduckgo-search yfinance lancedb tantivy pypdf agno` to install dependencies."""

from agno.agent import Agent
from agno.embedder.openai import OpenAIEmbedder
from agno.knowledge.pdf_url import PDFUrlKnowledgeBase
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.models.ollama import Ollama
from agno.embedder.ollama import OllamaEmbedder

print('-'*50)
print('Level 0: Agents with no tools (basic inference tasks).')
print('-'*50)
# Level 0: Agents with no tools (basic inference tasks).
level_0_agent = Agent(
    model=Ollama(id="llama3.2:latest"),
    description="You are an enthusiastic news reporter with a flair for storytelling!",
    markdown=True,
)
level_0_agent.print_response(
    "Tell me about a breaking news story from New York.", stream=True
)
print('-'*50)
print('Level 1: Agents with tools for autonomous task execution.')
print('-'*50)
# Level 1: Agents with tools for autonomous task execution.
level_1_agent = Agent(
    model=Ollama(id="llama3.2:latest"),
    description="You are an enthusiastic news reporter with a flair for storytelling!",
    tools=[DuckDuckGoTools()],
    show_tool_calls=True,
    markdown=True,
)
level_1_agent.print_response(
    "Tell me about a breaking news story from New York.", stream=True
)
print('-'*50)
print('Level 2: Agents with knowledge, combining memory and reasoning.')
print('-'*50)
# Level 2: Agents with knowledge, combining memory and reasoning.
level_2_agent = Agent(
    model=Ollama(id="llama3.2:latest"),
    description="You are a Thai cuisine expert!",
    instructions=[
        "Search your knowledge base for Thai recipes.",
        "If the question is better suited for the web, search the web to fill in gaps.",
        "Prefer the information in your knowledge base over the web results.",
    ],
    knowledge=PDFUrlKnowledgeBase(
        urls=["https://agno-public.s3.amazonaws.com/recipes/ThaiRecipes.pdf"],
        vector_db=LanceDb(
            uri="tmp/lancedb",
            table_name="recipes",
            search_type=SearchType.hybrid,
            embedder=OllamaEmbedder(id="nomic-embed-text"),
        ),
    ),
    tools=[DuckDuckGoTools()],
    show_tool_calls=True,
    markdown=True,
)

# Comment out after first run
# if level_2_agent.knowledge is not None:
#     level_2_agent.knowledge.load()
level_2_agent.print_response(
    "How do I make chicken and galangal in coconut milk soup", stream=True
)
level_2_agent.print_response("What is the history of Thai curry?", stream=True)

print('-'*50)
print('Level 3: Teams of agents collaborating on complex workflows.')
print('-'*50)
# Level 3: Teams of agents collaborating on complex workflows.
web_agent = Agent(
    name="Web Agent",
    role="Search the web for information",
    model=Ollama(id="llama3.2:latest"),
    tools=[DuckDuckGoTools()],
    instructions="Always include sources",
    show_tool_calls=True,
    markdown=True,
)

finance_agent = Agent(
    name="Finance Agent",
    role="Get financial data",
    model=Ollama(id="llama3.2:latest"),
    tools=[
        YFinanceTools(stock_price=True, analyst_recommendations=True, company_info=True)
    ],
    instructions="Use tables to display data",
    show_tool_calls=True,
    markdown=True,
)

level_3_agent_team = Agent(
    team=[web_agent, finance_agent],
    model=Ollama(id="llama3.2:latest"),
    instructions=["Always include sources", "Use tables to display data"],
    show_tool_calls=True,
    markdown=True,
)
level_3_agent_team.print_response(
    "What's the market outlook and financial performance of AI semiconductor companies?",
    stream=True,
)
