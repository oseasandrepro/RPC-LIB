from abc import ABC, abstractmethod

class RpcServerBinderInterface(ABC):

    @abstractmethod
    def start_binder(self):
        pass

    @abstractmethod
    def stop(self):
        pass