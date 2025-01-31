
from abc import ABC, abstractmethod

class BaseClient(ABC):
    @abstractmethod
    def get_client(self, source: str):
        pass
