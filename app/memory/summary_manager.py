class SummaryManager:
    """
    Stores a running summary of the conversation.
    """

    def __init__(self):
        self.summary = ""

    def get_summary(self):
        return self.summary

    def update_summary(self, new_summary):
        self.summary = new_summary

    def clear(self):
        self.summary = ""