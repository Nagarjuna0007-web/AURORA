from app.core.logger import logger


class ToolRegistry:
    """
    Registry for all tools available to AURORA.
    """

    def __init__(self):
        self.tools = {}

    def register(self, tool, capability=None):
        """
        Register a tool with AURORA.

        If a capability is provided, it becomes the
        lookup key used by the Capability Executor.
        """

        key = capability if capability else tool.name.lower()

        self.tools[key] = tool

        logger.info(
            f"Tool registered: {tool.name} | "
            f"Capability: {key}"
        )

    def get(self, name):
        """
        Retrieve a registered tool by capability or name.
        """

        return self.tools.get(name)

    def has(self, name):
        """
        Check whether a tool exists.
        """

        return name in self.tools

    def list_tools(self):
        """
        Return the registered tool capabilities.
        """

        return list(self.tools.keys())