class RpcException(Exception):
    """Base class for all RPC-related exceptions."""

    pass


class RpcCallException(RpcException):
    """Raised when the RPC server returns an error response."""

    def __init__(self, message, code=None):
        self.code = code
        self.message = message


class RpcBinderRequestException(RpcException):
    """Raised when the RPC server Binder returns an error response."""

    def __init__(self, message, code=None):
        self.code = code
        self.message = message


class RpcProcUnvailException(RpcException):
    """The program cannot support the requested procedure."""

    def __init__(self, message, code=None):
        self.code = code
        self.message = message
