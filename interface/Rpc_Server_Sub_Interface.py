from abc import ABC, abstractmethod

class RpcServerStubInterface(ABC):

    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def start(self):
        pass