from app.agents.base_agent import BaseAgent


class AssistantAgent(BaseAgent):

    def __init__(self, name, model):
        super().__init__(name)
        self.model = model

    def process(self, messages):
        """
        Generate a complete response.
        """
        return self.model.generate(messages)

    def stream(self, user_input):
        """
        Stream the response chunk by chunk.
        """

        messages = [
            {
                "role": "user",
                "content": user_input
            }
        ]

        return self.model.stream(messages)