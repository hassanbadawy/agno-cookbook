import asyncio

from agno.agent import Agent, RunResponse
from agno.tools.duckduckgo import DuckDuckGoTools
from rich.pretty import pprint
from agno.models.ollama import Ollama
model=Ollama(id="llama3.2:latest")
providers = ["openai", "anthropic", "ollama", "cohere", "google"]
instructions = [
    "Your task is to write a well researched report on AI providers.",
    "The report should be unbiased and factual.",
]


async def get_agent(delay, provider):
    agent = Agent(
        model=model,
        instructions=instructions,
        tools=[DuckDuckGoTools()],
    )
    await asyncio.sleep(delay)
    response: RunResponse = await agent.arun(
        f"Write a report on the following AI provider: {provider}"
    )
    return response


async def get_reports():
    tasks = []
    for delay, provider in enumerate(providers):
        delay = delay * 2
        tasks.append(get_agent(delay, provider))

    results = await asyncio.gather(*tasks)
    return results


async def main():
    results = await get_reports()
    for result in results:
        print("************")
        pprint(result.content)
        print("************")
        print("\n")


if __name__ == "__main__":
    asyncio.run(main())
