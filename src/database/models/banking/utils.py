from enum import Enum


class TransferStatus(str, Enum):
    processing = "processing"
    completed = "completed"
    aborted = "aborted"