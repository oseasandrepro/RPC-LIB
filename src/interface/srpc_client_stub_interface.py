from abc import ABC, abstractmethod

class SrpcClientStubInterface(ABC):

    @abstractmethod
    def remote_call(self, func_name, parameters: tuple):
        pass