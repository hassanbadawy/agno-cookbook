import asyncio

from agno.agent import Agent
from agno.models.ollama import Ollama
from agno.models.openai import OpenAIChat

model_base_url = "http://localhost:11434/v1/"  # chat/completions
model_id = "qwen3:0.6b"  # Ollama model ID
model=OpenAIChat(id=model_id, base_url=model_base_url, api_key="123")
agent = Agent(
    model=model,
    description="You help people with their health and fitness goals.",
    instructions=["Recipes should be under 5 ingredients"],
    markdown=True,
)
# -*- Print a response to the cli
asyncio.run(agent.aprint_response("Share a breakfast recipe."))
