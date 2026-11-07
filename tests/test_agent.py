from app.models.ollama_model import OllamaModel
from app.agents.assistant_agent import AssistantAgent

model = OllamaModel()

agent = AssistantAgent(
    name="Assistant",
    model=model
)

messages = [
    {
        "role": "User",
        "message": "Hello AURORA!"
    }
]

response = agent.process(messages)

print(response)