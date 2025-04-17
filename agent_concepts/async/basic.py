import asyncio

from agno.agent import Agent
from agno.models.ollama import Ollama
model=Ollama(id="llama3.2:latest")
agent = Agent(
    model=model,
    description="You help people with their health and fitness goals.",
    instructions=["Recipes should be under 5 ingredients"],
    markdown=True,
)
# -*- Print a response to the cli
asyncio.run(agent.aprint_response("Share a breakfast recipe."))
