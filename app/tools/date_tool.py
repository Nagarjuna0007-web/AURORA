from datetime import datetime

from app.tools.base_tool import BaseTool


class DateTool(BaseTool):
    """
    Tool that returns the current local system date.
    """

    def __init__(self):
        super().__init__("Date")

    def execute(self, *args, **kwargs):
        """
        Return the current local date.
        """

        today = datetime.now()

        return today.strftime(
            "%Y-%m-%d"
        )