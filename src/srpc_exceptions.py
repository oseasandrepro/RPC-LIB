class SrpcException(Exception):
    """Base class for all RPC-related exceptions."""

    pass


class SrpcCallException(SrpcException):
    """Raised when the RPC server returns an error response."""

    def __init__(self, message, code=None):
        self.code = code
        self.message = message


class SrpcBinderRequestException(SrpcException):
    """Raised when the RPC server Binder returns an error response."""

    def __init__(self, message, code=None):
        self.code = code
        self.message = message


class SrpcProcUnvailException(SrpcException):
    """The program cannot support the requested procedure."""

    def __init__(self, message, code=None):
        self.code = code
        self.message = message
