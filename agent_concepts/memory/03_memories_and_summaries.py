"""
This recipe shows how to store personalized memories and summaries in a sqlite database.
Steps:
1. Run: `pip install openai sqlalchemy agno` to install dependencies
2. Run: `python cookbook/memory/03_memories_and_summaries.py` to run the agent
"""
import os
os.environ["OLLAMA_MODEL_ID"] = "llama3.2:latest"


import json
from agno.agent import Agent, AgentMemory
from agno.memory.db.sqlite import SqliteMemoryDb
from agno.storage.agent.sqlite import SqliteAgentStorage
from rich.console import Console
from rich.json import JSON
from rich.panel import Panel
from agno.models.ollama import Ollama
from agno.memory.classifier import MemoryClassifier
from agno.memory.summarizer import MemorySummarizer
import os

ollama_model = Ollama(id=os.environ.get("OLLAMA_MODEL_ID", "llama3.2:latest"))

agent = Agent(
    model=ollama_model,
    # The memories are personalized for this user
    user_id="john_billings",
    # Store the memories and summary in a table: agent_memory
    memory=AgentMemory(
        db=SqliteMemoryDb(
            table_name="agent_memory",
            db_file="tmp/agent_memory.db",
        ),
        # Create and store personalized memories for this user
        create_user_memories=False,
        # Update memories for the user after each run
        update_user_memories_after_run=False,
        # Create and store session summaries
        create_session_summary=True,
        # Update session summaries after each run
        update_session_summary_after_run=True,
        summarizer=MemorySummarizer(model=ollama_model),
        classifier=MemoryClassifier(model=ollama_model),
    ),
    # Store agent sessions in a database, that persists between runs
    storage=SqliteAgentStorage(
        table_name="agent_sessions", db_file="tmp/agent_storage.db"
    ),
    # add_history_to_messages=true adds the chat history to the messages sent to the Model.
    add_history_to_messages=True,
    # Number of historical responses to add to the messages.
    num_history_responses=3,
    # Description creates a system prompt for the agent
    description="You are a helpful assistant that always responds in a polite, upbeat and positive manner.",
)

console = Console()


def render_panel(title: str, content: str) -> Panel:
    try:
        # Try to parse content as JSON
        return Panel(JSON(content, indent=4), title=title, expand=True)
    except json.JSONDecodeError:
        # If content is not valid JSON, just display it as plain text
        return Panel(content, title=title, expand=True)
    
def print_agent_memory(agent):
    # -*- Print history
    console.print(
        render_panel(
            f"Chat History for session_id: {agent.session_id}",
            json.dumps(
                [
                    m.model_dump(include={"role", "content"})
                    for m in agent.memory.messages
                ],
                indent=4,
            ),
        )
    )
    # -*- Print memories
    memories_data = "[]"
    if agent.memory.memories:
        memories_data = json.dumps(
            [
                m.model_dump(include={"memory", "input"})
                for m in agent.memory.memories
            ],
            indent=4,
        )
    console.print(
        render_panel(
            f"Memories for user_id: {agent.user_id}",
            memories_data,
        )
    )
    # -*- Print summary
    summary_data = "No summary available"
    if agent.memory.summary:
        summary_data = json.dumps(agent.memory.summary.model_dump(), indent=4)
    console.print(
        render_panel(
            f"Summary for session_id: {agent.session_id}",
            summary_data,
        )
    )

# -*- Share personal information
agent.print_response("My name is john billings and I live in nyc.", stream=True)
# -*- Print agent memory
print_agent_memory(agent)

# -*- Share personal information
agent.print_response("I'm going to a concert tomorrow?", stream=True)
# -*- Print agent memory
print_agent_memory(agent)

# Ask about the conversation
agent.print_response(
    "What have we been talking about, do you know my name?", stream=True
)
