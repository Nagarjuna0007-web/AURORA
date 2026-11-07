from app.prompts.prompt_builder import build_prompt

history = """
User: Hello
Aurora: Hi! How can I help you?
"""

prompt = build_prompt(
    history,
    "Explain machine learning."
)

print(prompt)