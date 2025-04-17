import sqlalchemy
from sqlalchemy import text

# Use the same database connection string from your application
db_url = "postgresql+psycopg://ai:ai@localhost:5532/ai"

# Create engine
engine = sqlalchemy.create_engine(db_url)

# Drop the vector table
with engine.connect() as connection:
    # Start a transaction
    with connection.begin():
        # Drop the table
        connection.execute(text("DROP TABLE IF EXISTS ai.agentic_rag_documents"))
        print("Table ai.agentic_rag_documents dropped successfully.")
        
        # Optional: If you need to recreate the schema too
        # connection.execute(text("DROP SCHEMA IF EXISTS ai CASCADE"))
        # connection.execute(text("CREATE SCHEMA ai"))
        # print("Schema ai recreated.")

print("Database reset complete. The table will be recreated with correct dimensions on next application run.")