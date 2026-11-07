from app.tools.time_tool import TimeTool


def main():

    tool = TimeTool()

    result = tool.execute()

    print("\n========== TIME TOOL ==========\n")
    print(f"Tool   : {tool.name}")
    print(f"Result : {result}")


if __name__ == "__main__":
    main()