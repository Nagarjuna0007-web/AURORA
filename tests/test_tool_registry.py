from app.tools.calculator_tool import CalculatorTool
from app.tools.time_tool import TimeTool
from app.tools.date_tool import DateTool
from app.tools.tool_registry import ToolRegistry


def main():

    registry = ToolRegistry()

    calculator = CalculatorTool()
    time_tool = TimeTool()
    date_tool = DateTool()

    registry.register(calculator)
    registry.register(time_tool)
    registry.register(date_tool)

    print("Registered Tools:")

    for tool in registry.list_tools():
        print("-", tool)

    print("\nDate Tool Result:")
    print(registry.get("Date").execute())


if __name__ == "__main__":
    main()