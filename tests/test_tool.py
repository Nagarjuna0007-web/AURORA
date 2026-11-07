from app.tools.calculator_tool import CalculatorTool


tool = CalculatorTool()

expressions = [
    "25 + 18",
    "10 * 5",
    "100 / 4",
    "2 ** 3",
    "(10 + 5) * 2",
]

print("\n========== CALCULATOR TEST ==========\n")

for expression in expressions:
    result = tool.execute(expression)

    print(f"Expression : {expression}")
    print(f"Result     : {result}")
    print()