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