from abc import ABC, abstractmethod

class SrpcServerBinderInterface(ABC):

    @abstractmethod
    def start_binder(self):
        pass

    @abstractmethod
    def stop(self):
        pass