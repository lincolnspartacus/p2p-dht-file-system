# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import chord_pb2 as chord__pb2


class ChordServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.findSuccessor = channel.unary_unary(
                '/ChordService/findSuccessor',
                request_serializer=chord__pb2.FindSuccessorRequest.SerializeToString,
                response_deserializer=chord__pb2.FindSuccessorResponse.FromString,
                )


class ChordServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def findSuccessor(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_ChordServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'findSuccessor': grpc.unary_unary_rpc_method_handler(
                    servicer.findSuccessor,
                    request_deserializer=chord__pb2.FindSuccessorRequest.FromString,
                    response_serializer=chord__pb2.FindSuccessorResponse.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'ChordService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class ChordService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def findSuccessor(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/ChordService/findSuccessor',
            chord__pb2.FindSuccessorRequest.SerializeToString,
            chord__pb2.FindSuccessorResponse.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)


class BootstrapServiceStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.getNode = channel.unary_unary(
                '/BootstrapService/getNode',
                request_serializer=chord__pb2.Empty.SerializeToString,
                response_deserializer=chord__pb2.NodeInfo.FromString,
                )
        self.addNode = channel.unary_unary(
                '/BootstrapService/addNode',
                request_serializer=chord__pb2.NodeInfo.SerializeToString,
                response_deserializer=chord__pb2.Empty.FromString,
                )
        self.clearTable = channel.unary_unary(
                '/BootstrapService/clearTable',
                request_serializer=chord__pb2.Empty.SerializeToString,
                response_deserializer=chord__pb2.Empty.FromString,
                )


class BootstrapServiceServicer(object):
    """Missing associated documentation comment in .proto file."""

    def getNode(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def addNode(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')

    def clearTable(self, request, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_BootstrapServiceServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'getNode': grpc.unary_unary_rpc_method_handler(
                    servicer.getNode,
                    request_deserializer=chord__pb2.Empty.FromString,
                    response_serializer=chord__pb2.NodeInfo.SerializeToString,
            ),
            'addNode': grpc.unary_unary_rpc_method_handler(
                    servicer.addNode,
                    request_deserializer=chord__pb2.NodeInfo.FromString,
                    response_serializer=chord__pb2.Empty.SerializeToString,
            ),
            'clearTable': grpc.unary_unary_rpc_method_handler(
                    servicer.clearTable,
                    request_deserializer=chord__pb2.Empty.FromString,
                    response_serializer=chord__pb2.Empty.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'BootstrapService', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class BootstrapService(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def getNode(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/BootstrapService/getNode',
            chord__pb2.Empty.SerializeToString,
            chord__pb2.NodeInfo.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def addNode(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/BootstrapService/addNode',
            chord__pb2.NodeInfo.SerializeToString,
            chord__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)

    @staticmethod
    def clearTable(request,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.unary_unary(request, target, '/BootstrapService/clearTable',
            chord__pb2.Empty.SerializeToString,
            chord__pb2.Empty.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)
