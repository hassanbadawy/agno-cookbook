"""Run `pip install duckdb` to install dependencies."""

import asyncio
from textwrap import dedent

from agno.agent import Agent
from agno.tools.duckdb import DuckDbTools
from agno.models.ollama import Ollama
model=Ollama(id="llama3.2:latest")

duckdb_tools = DuckDbTools(
    create_tables=False, export_tables=False, summarize_tables=False
)
duckdb_tools.create_table_from_path(
    path="https://agno-public.s3.amazonaws.com/demo_data/IMDB-Movie-Data.csv",
    table="movies",
)

agent = Agent(
    model=model,
    tools=[duckdb_tools],
    markdown=True,
    show_tool_calls=True,
    additional_context=dedent("""\
    You have access to the following tables:
    - movies: contains information about movies from IMDB.
    """),
)
asyncio.run(agent.aprint_response("What is the average rating of movies?"))
