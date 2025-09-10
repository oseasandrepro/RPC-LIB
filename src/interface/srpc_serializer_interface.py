from abc import ABC, abstractmethod


class SrpcSerializerInterface(ABC):

    @abstractmethod
    def serialize(self, data):
        pass

    @abstractmethod
    def deserialize(self, data):
        pass
