from abc import ABC, abstractmethod

class RpcServerBinderInterface(ABC):

    @abstractmethod
    def binding_lookup(self):
        pass