from abc import ABC, abstractmethod


class SrpcClientBinderInterface(ABC):

    @abstractmethod
    def binding_lookup(self):
        pass
