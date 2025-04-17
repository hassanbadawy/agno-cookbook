import asyncio

from agno.agent import Agent
from agno.cli.console import console
from agno.models.ollama import Ollama
model=Ollama(id="llama3.2:latest")
model_reasoning=Ollama(id="deepseek-r1:8b")

task = "9.11 and 9.9 -- which is bigger?"

regular_agent = Agent(model=model, markdown=True)
reasoning_agent = Agent(
    model=model_reasoning,
    reasoning=True,
    markdown=True,
    structured_outputs=True,
)

console.rule("[bold green]Regular Agent[/bold green]")
asyncio.run(regular_agent.aprint_response(task, stream=True))
console.rule("[bold yellow]Reasoning Agent[/bold yellow]")
asyncio.run(
    reasoning_agent.aprint_response(task, stream=True, show_full_reasoning=True)
)