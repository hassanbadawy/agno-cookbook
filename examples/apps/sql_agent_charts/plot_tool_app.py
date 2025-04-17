import pandas as pd
import matplotlib.pyplot as plt
from agno.tools import Tool
from agno.agent import Agent
from agno.models.openai import OpenAIChat
import sqlite3
import streamlit as st
import os

# Define the custom PlotTool class
class PlotTool(Tool):
    def __init__(self, db_path: str):
        super().__init__(name="plot_tool", description="Generates plots based on SQL queries and user-specified plot types.")
        self.db_path = db_path

    def execute(self, input_data: dict, plot_type: str) -> dict:
        df = pd.DataFrame(input_data)

        try:
            # Create the plot based on the specified plot type
            fig, ax = plt.subplots()
            if plot_type == "bar":
                df.plot(kind="bar", ax=ax)
            elif plot_type == "line":
                df.plot(kind="line", ax=ax)
            elif plot_type == "scatter":
                df.plot(kind="scatter", ax=ax)
            else:
                return {"error": f"Unsupported plot type: {plot_type}"}
            # Return the plot figure
            return {"plot": fig}
        except Exception as e:
            return {"error": f"Plotting failed: {str(e)}"}

# Set up the Agno agent
agent = Agent(
    name="PlotAgent",
    role="You are a data visualization assistant. When a user requests a plot, determine the plot type, generate the necessary SQL query, specify the x and y columns, and use the PlotTool to generate the plot.",
    model=OpenAIChat(api_key=os.environ["OPENAI_API_KEY"]),
    tools=[PlotTool(db_path="path/to/your/database.db")]  # Replace with actual database path
)

# Streamlit app
st.title("Plot Generator")

# User input for the plot request
user_input = st.text_input("Enter your plot request (e.g., 'plot a bar chart of sales by region'):")

if st.button("Generate Plot"):
    # Run the agent with the user's input
    response = agent.run({"query": user_input})
    
    # Display the plot if present in the response
    if "plot" in response:
        st.pyplot(response["plot"])
    
    # Display any additional answer or error messages
    if "answer" in response:
        st.write(response["answer"])
    if "error" in response:
        st.error(response["error"])