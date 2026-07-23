import msgpack

from ..interface.srpc_serializer_interface import SrpcSerializerInterface


class SrpcSerializer(SrpcSerializerInterface):
    def serialize(self, data):
        return msgpack.packb(data)

    def deserialize(self, data):
        deserialized_data = msgpack.unpackb(data)
        return deserialized_data
