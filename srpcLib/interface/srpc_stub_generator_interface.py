from abc import ABC, abstractmethod


class SrpcStubGeneratorInterface(ABC):
    @abstractmethod
    def generate_stub(self, dest_path: str):
        pass

    @abstractmethod
    def get_type() -> str:
        pass

    @abstractmethod
    def get_lenguage() -> str:
        pass
