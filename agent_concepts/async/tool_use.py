import asyncio

from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.models.ollama import Ollama
model=Ollama(id="llama3.2:latest")
model2=Ollama(id="gemma3:latest")
agent = Agent(
    model=model,
    tools=[DuckDuckGoTools()],
    show_tool_calls=True,
    markdown=True,
)
asyncio.run(agent.aprint_response("Whats happening in UK and in USA?"))
