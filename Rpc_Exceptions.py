class RpcException(Exception):
    """Base class for all RPC-related exceptions."""
    pass

class RpcCallException(RpcException):
    """Raised when the RPC server returns an error response."""
    def __init__(self, message, code=None):
        self.code = code
        self.message = message

class RpcTransportException(RpcException):
    """Raised when transport-level errors occur (e.g., connection, timeout)."""
    pass


class RpcBinderRequestException(RpcException):
    """Raised when the RPC server Binder returns an error response."""
    def __init__(self, message, code=None):
        self.code = code
        self.message = message