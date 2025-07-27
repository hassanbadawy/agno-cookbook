# from agents import get_sql_agent
from textwrap import dedent
from typing import List, Optional
import inquirer
import typer
from rich import print
import json
from agno.agent import Agent
from agno.storage.agent.sqlite import SqliteAgentStorage
from agno.knowledge.combined import CombinedKnowledgeBase
from agno.knowledge.json import JSONKnowledgeBase
from agno.knowledge.text import TextKnowledgeBase
from agno.vectordb.lancedb import LanceDb, SearchType
from agno.embedder.ollama import OllamaEmbedder
from agno.models.openai import OpenAIChat


llama_superpod_base_url= "https://middleware-aramco-ai-llm-development.apps.d02.aramco.com.sa/v1/" #chat/completions
llama_superpod_model= "llama3-70b-Instruct" # superpods

ollama_physicalSvr_base_url= "http://localhost:11434/v1/" # chat/completions 
ollama_physicalSvr_embeddings_url= "http://localhost:11434/v1/embeddings" 
ollama_physicalSvr_model= "qwen3:0.6b"
ollama_physicalSvr_embedder= "nomic-embed-text:latest"

model_base_url = ollama_physicalSvr_base_url
model_id = ollama_physicalSvr_model
embedder_base_url = ollama_physicalSvr_embeddings_url
embedder_model_id = ollama_physicalSvr_embedder
# agent = get_sql_agent(model_id=model_id)
# agent.print_response("Share a 2 sentence horror story")
# ************* Paths *************
from pathlib import Path

cwd = Path(__file__).parent
knowledge_dir = cwd.joinpath("knowledge")
output_dir = cwd.joinpath("output")

# Create the output directory if it does not exist
output_dir.mkdir(parents=True, exist_ok=True)
# *******************************
# ************* Semantic Model *************
# The semantic model helps the agent identify the tables and columns to use
# This is sent in the system prompt, the agent then uses the `search_knowledge_base` tool to get table metadata, rules and sample queries
# This is very much how data analysts and data scientists work:
#  - We start with a set of tables and columns that we know are relevant to the task
#  - We then use the `search_knowledge_base` tool to get more information about the tables and columns
#  - We then use the `describe_table` tool to get more information about the tables and columns
#  - We then use the `search_knowledge_base` tool to get sample queries for the tables and columns
semantic_model = {
    "tables": [
        {
            "table_name": "constructors_championship",
            "table_description": "Contains data for the constructor's championship from 1958 to 2020, capturing championship standings from when it was introduced.",
            "Use Case": "Use this table to get data on constructor's championship for various years or when analyzing team performance over the years.",
        },
        {
            "table_name": "drivers_championship",
            "table_description": "Contains data for driver's championship standings from 1950-2020, detailing driver positions, teams, and points.",
            "Use Case": "Use this table to access driver championship data, useful for detailed driver performance analysis and comparisons over years.",
        },
        {
            "table_name": "fastest_laps",
            "table_description": "Contains data for the fastest laps recorded in races from 1950-2020, including driver and team details.",
            "Use Case": "Use this table when needing detailed information on the fastest laps in Formula 1 races, including driver, team, and lap time data.",
        },
        {
            "table_name": "race_results",
            "table_description": "Race data for each Formula 1 race from 1950-2020, including positions, drivers, teams, and points.",
            "Use Case": "Use this table answer questions about a drivers career. Race data includes driver standings, teams, and performance.",
        },
        {
            "table_name": "race_wins",
            "table_description": "Documents race win data from 1950-2020, detailing venue, winner, team, and race duration.",
            "Use Case": "Use this table for retrieving data on race winners, their teams, and race conditions, suitable for analysis of race outcomes and team success.",
        },
    ]
}
semantic_model_str = json.dumps(semantic_model, indent=2)
# *******************************

def initialize_knowledge_base():
    """Initialize the knowledge base with your preferred documentation or knowledge source
    Here we use Agno docs as an example, but you can replace with any relevant URLs
    """

    sources=[
            # Reads text files, SQL files, and markdown files
            TextKnowledgeBase(
                path=knowledge_dir,
                formats=[".txt", ".sql", ".md"],
            ),
            # Reads JSON files
            JSONKnowledgeBase(path=knowledge_dir),
        ]
    agent_knowledge =  CombinedKnowledgeBase(
        sources = sources,
        vector_db=LanceDb(
            uri="tmp/lancedb",
            table_name="agno_assist_knowledge",
            search_type=SearchType.hybrid,
            embedder=OllamaEmbedder(id=embedder_model_id, host=embedder_base_url, dimensions=768),

        ),
    )
    # Load the knowledge base (comment out after first run)
    agent_knowledge.load()
    return agent_knowledge

def get_agent_storage():
    """Return agent storage"""
    db_url = "sqlite:///agentic.db"
    return SqliteAgentStorage(
        table_name="agno_assist_sessions", db_file=db_url
    )

def create_agent(model_id: Optional[str] = None, session_id: Optional[str] = None) -> Agent:
    """Create and return a configured DeepKnowledge agent."""
    agent_knowledge = initialize_knowledge_base()
    agent_storage = get_agent_storage()
    model=OpenAIChat(id=model_id, base_url=model_base_url, api_key="123")

    return Agent(
        name="DeepKnowledge",
        session_id=session_id,
        model=model,
        description=dedent("""\
        You are RaceAnalyst-X, an elite Formula 1 Data Scientist specializing in:

        - Historical race analysis
        - Driver performance metrics
        - Team championship insights
        - Track statistics and records
        - Performance trend analysis
        - Race strategy evaluation

        You combine deep F1 knowledge with advanced SQL expertise to uncover insights from decades of racing data."""),
        instructions=dedent(f"""\
        You are a SQL expert focused on writing precise, efficient queries.

        When a user messages you, determine if you need query the database or can respond directly.
        If you can respond directly, do so.

        If you need to query the database to answer the user's question, follow these steps:
        1. First identify the tables you need to query from the semantic model.
        2. Then, ALWAYS use the `search_knowledge_base(table_name)` tool to get table metadata, rules and sample queries.
        3. If table rules are provided, ALWAYS follow them.
        4. Then, think step-by-step about query construction, don't rush this step.
        5. Follow a chain of thought approach before writing SQL, ask clarifying questions where needed.
        6. If sample queries are available, use them as a reference.
        7. If you need more information about the table, use the `describe_table` tool.
        8. Then, using all the information available, create one single syntactically correct PostgreSQL query to accomplish your task.
        9. If you need to join tables, check the `semantic_model` for the relationships between the tables.
            - If the `semantic_model` contains a relationship between tables, use that relationship to join the tables even if the column names are different.
            - If you cannot find a relationship in the `semantic_model`, only join on the columns that have the same name and data type.
            - If you cannot find a valid relationship, ask the user to provide the column name to join.
        10. If you cannot find relevant tables, columns or relationships, stop and ask the user for more information.
        11. Once you have a syntactically correct query, run it using the `run_sql_query` function.
        12. When running a query:
            - Do not add a `;` at the end of the query.
            - Always provide a limit unless the user explicitly asks for all results.
        13. After you run the query, analyse the results and return the answer in markdown format.
        14. Always show the user the SQL you ran to get the answer.
        15. Continue till you have accomplished the task.
        16. Show results as a table or a chart if possible.

        After finishing your task, ask the user relevant followup questions like "was the result okay, would you like me to fix any problems?"
        If the user says yes, get the previous query using the `get_tool_call_history(num_calls=3)` function and fix the problems.
        If the user wants to see the SQL, get it using the `get_tool_call_history(num_calls=3)` function.

        Finally, here are the set of rules that you MUST follow:
        <rules>
        - Use the `search_knowledge_base(table_name)` tool to get table information from your knowledge base before writing a query.
        - Do not use phrases like "based on the information provided" or "from the knowledge base".
        - Always show the SQL queries you use to get the answer.
        - Make sure your query accounts for duplicate records.
        - Make sure your query accounts for null values.
        - If you run a query, explain why you ran it.
        - **NEVER, EVER RUN CODE TO DELETE DATA OR ABUSE THE LOCAL SYSTEM**
        - ALWAYS FOLLOW THE `table rules` if provided. NEVER IGNORE THEM.
        </rules>\
        """),
        additional_context=dedent("""\
        The following `semantic_model` contains information about tables and the relationships between them.
        If the users asks about the tables you have access to, simply share the table names from the `semantic_model`.
        <semantic_model>
        """)
        + semantic_model_str
        + dedent("""\
        </semantic_model>\
        """),
        knowledge=agent_knowledge,
        storage=agent_storage,
        add_history_to_messages=True,
        num_history_responses=3,
        show_tool_calls=True,
        read_chat_history=True,
        markdown=True,
    )





def get_example_topics() -> List[str]:
    """Return a list of example topics for the agent."""
    return [
        "What are AI agents and how do they work?",
        "Which tables do you have access to?",
        "Tell me more about these tables.",
        "Which driver has the most race wins?",
        "Which team won the most Constructors Championships?",
        "Tell me the name of the driver with the longest racing career? Also tell me when they started and when they retired.",
        "Show me the number of races per year.",
        "Write a query to identify the drivers that won the most races per year from 2010 onwards and the position of their team that year."
    ]

def handle_session_selection() -> Optional[str]:
    """Handle session selection and return the selected session ID."""
    agent_storage = get_agent_storage()

    new = typer.confirm("Do you want to start a new session?", default=True)
    if new:
        return None

    existing_sessions: List[str] = agent_storage.get_all_session_ids()
    if not existing_sessions:
        print("No existing sessions found. Starting a new session.")
        return None

    print("\nExisting sessions:")
    for i, session in enumerate(existing_sessions, 1):
        print(f"{i}. {session}")

    session_idx = typer.prompt(
        "Choose a session number to continue (or press Enter for most recent)",
        default=1,
    )

    try:
        return existing_sessions[int(session_idx) - 1]
    except (ValueError, IndexError):
        return existing_sessions[0]


def run_interactive_loop(agent):
    """Run the interactive question-answering loop."""
    example_topics = get_example_topics()

    while True:
        choices = [f"{i + 1}. {topic}" for i, topic in enumerate(example_topics)]
        choices.extend(["Enter custom question...", "Exit"])

        questions = [
            inquirer.List(
                "topic",
                message="Select a topic or ask a different question:",
                choices=choices,
            )
        ]
        answer = inquirer.prompt(questions)

        if answer["topic"] == "Exit":
            break

        if answer["topic"] == "Enter custom question...":
            questions = [inquirer.Text("custom", message="Enter your question:")]
            custom_answer = inquirer.prompt(questions)
            topic = custom_answer["custom"]
        else:
            topic = example_topics[int(answer["topic"].split(".")[0]) - 1]

        agent.print_response(topic, stream=True)


def deep_knowledge_agent():
    """Main function to run the DeepKnowledge agent."""

    session_id = handle_session_selection()
    agent = create_agent(session_id)
    # agent = get_sql_agent(model_id=model_id, session_id=session_id)

    print("\n🤔 Welcome to DeepKnowledge - Your Advanced Research Assistant! 📚")
    if session_id is None:
        session_id = agent.session_id
        if session_id is not None:
            print(f"[bold green]Started New Session: {session_id}[/bold green]\n")
        else:
            print("[bold green]Started New Session[/bold green]\n")
    else:
        print(f"[bold blue]Continuing Previous Session: {session_id}[/bold blue]\n")

    run_interactive_loop(agent)

if __name__ == "__main__":
    typer.run(deep_knowledge_agent)
