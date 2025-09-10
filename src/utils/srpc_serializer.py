import pickle

from interface.srpc_serializer_interface import SrpcSerializerInterface


class SrpcSerializer(SrpcSerializerInterface):
    def serialize(self, data):
        return pickle.dumps(data)

    def deserialize(self, data):
        deserialized_data = pickle.loads(data)
        return deserialized_data
