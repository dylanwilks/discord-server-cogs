from enum import Enum


class Alerts(Enum):
    def __str__(self):
        return self.value

    NO_COMMAND_PERM = "You do not have permission for this command."
    SERVER_NOT_FOUND = "Specified server not found."
    STARTUP = "Bot started. Type !help for a list of commands."
    SERVER_UNRESPONSIVE = "No response from server. Command not sent."
