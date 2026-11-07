from datetime import datetime

from app.tools.base_tool import BaseTool


class TimeTool(BaseTool):
    """
    Tool that returns the current local system date and time.
    """

    def __init__(self):
        super().__init__("Time")

    def execute(self, *args, **kwargs):
        """
        Return the current local date and time.
        """

        now = datetime.now()

        return now.strftime(
            "%Y-%m-%d %H:%M:%S"
        )