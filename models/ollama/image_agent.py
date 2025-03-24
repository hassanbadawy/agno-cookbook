from pathlib import Path

from agno.agent import Agent
from agno.media import Image
from agno.models.ollama import Ollama

agent = Agent(
    model=Ollama(id="llama3.2-vision"),
    markdown=True,
)

image_path = Path(__file__).parent.joinpath("super-agents.png")
image_path = "http://localhost:8003/demo.jpeg"
response = agent.print_response(
    "describe the image",
    images=[Image(filepath=image_path)],
)
