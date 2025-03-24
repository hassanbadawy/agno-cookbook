from agno.agent import Agent, RunResponse  # noqa
from agno.models.google import Gemini
def export_env_variable(key, value):
    import subprocess
    command = f'export {key}={value}'
    subprocess.run(command, shell=True, check=True)
    print(f"Environment variable {key} exported successfully")
export_env_variable('GOOGLE_API_KEY', 'AIzaSyD7YtZHaNH1I_o7VlGi2UDylpAe5gwTlh8')

agent = Agent(model=Gemini(id="gemini-2.0-flash-exp"), markdown=True)

# Get the response in a variable
# run: RunResponse = agent.run("Share a 2 sentence horror story")
# print(run.content)

# Print the response in the terminal
agent.print_response("Share a 2 sentence horror story")
