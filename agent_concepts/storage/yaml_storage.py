"""Run `pip install duckduckgo-search openai` to install dependencies."""

from agno.agent import Agent
from agno.storage.agent.yaml import YamlAgentStorage
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.models.ollama import Ollama
from agno.embedder.ollama import OllamaEmbedder

model=Ollama(id="llama3.2:latest")
embedder=OllamaEmbedder(id="nomic-embed-text:latest", dimensions=768) 
agent = Agent(
    model=model,
    storage=YamlAgentStorage(dir_path="tmp/agent_sessions_yaml"),
    tools=[DuckDuckGoTools()],
    add_history_to_messages=True,
)
agent.print_response("How many people live in Canada?")
agent.print_response("What is their national anthem called?")
