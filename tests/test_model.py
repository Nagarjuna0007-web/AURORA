from app.agents.assistant_agent import AssistantAgent
from app.models.ollama_model import OllamaModel


model = OllamaModel()

agent = AssistantAgent("Assistant", model)

messages = [
    {
        "role": "user",
        "content": "Hello! AURORA!"
    }
]

response = agent.process(messages)

print(response)