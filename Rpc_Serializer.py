import pickle
from interface.Rpc_Serializer_Interface import RpcSerializerInterface

class RpcSerializer(RpcSerializerInterface):
    def serialize(self, data):
        return pickle.dumps(data)
    
    def deserialize(self, data):
         deserialized_data = pickle.loads(data)
         return deserialized_data