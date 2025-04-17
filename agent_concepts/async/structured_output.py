import asyncio
from typing import List

from agno.agent import Agent, RunResponse  # noqa
from pydantic import BaseModel, Field
from rich.pretty import pprint  # noqa
from agno.models.ollama import Ollama
model=Ollama(id="llama3.2:latest")
model2=Ollama(id="gemma3:latest")


class MovieScript(BaseModel):
    setting: str = Field(
        ..., description="Provide a nice setting for a blockbuster movie."
    )
    ending: str = Field(
        ...,
        description="Ending of the movie. If not available, provide a happy ending.",
    )
    genre: str = Field(
        ...,
        description="Genre of the movie. If not available, select action, thriller or romantic comedy.",
    )
    name: str = Field(..., description="Give a name to this movie")
    characters: List[str] = Field(..., description="Name of characters for this movie.")
    storyline: str = Field(
        ..., description="3 sentence storyline for the movie. Make it exciting!"
    )


# Agent that uses JSON mode
json_mode_agent = Agent(
    model=model,
    description="You write movie scripts.",
    response_model=MovieScript,
)

# Agent that uses structured outputs
structured_output_agent = Agent(
    model=model,
    description="You write movie scripts.",
    response_model=MovieScript,
    structured_outputs=True,
)


# Get the response in a variable
# json_mode_response: RunResponse = json_mode_agent.arun("New York")
# pprint(json_mode_response.content)
# structured_output_response: RunResponse = structured_output_agent.arun("New York")
# pprint(structured_output_response.content)

asyncio.run(json_mode_agent.aprint_response("New York"))
asyncio.run(structured_output_agent.aprint_response("New York"))
