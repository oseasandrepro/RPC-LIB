from abc import ABC, abstractmethod


class SrpcServerStubInterface(ABC):
    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def start(self):
        pass
