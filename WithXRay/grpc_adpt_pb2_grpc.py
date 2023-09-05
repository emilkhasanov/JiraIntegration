# Generated by the gRPC Python protocol compiler plugin. DO NOT EDIT!
"""Client and server classes corresponding to protobuf-defined services."""
import grpc

import grpc_adpt_pb2 as grpc__adpt__pb2


class GrpcAdapterStub(object):
    """Missing associated documentation comment in .proto file."""

    def __init__(self, channel):
        """Constructor.

        Args:
            channel: A grpc.Channel.
        """
        self.streamData = channel.stream_stream(
                '/GrpcAdapter/streamData',
                request_serializer=grpc__adpt__pb2.Request.SerializeToString,
                response_deserializer=grpc__adpt__pb2.Response.FromString,
                )


class GrpcAdapterServicer(object):
    """Missing associated documentation comment in .proto file."""

    def streamData(self, request_iterator, context):
        """Missing associated documentation comment in .proto file."""
        context.set_code(grpc.StatusCode.UNIMPLEMENTED)
        context.set_details('Method not implemented!')
        raise NotImplementedError('Method not implemented!')


def add_GrpcAdapterServicer_to_server(servicer, server):
    rpc_method_handlers = {
            'streamData': grpc.stream_stream_rpc_method_handler(
                    servicer.streamData,
                    request_deserializer=grpc__adpt__pb2.Request.FromString,
                    response_serializer=grpc__adpt__pb2.Response.SerializeToString,
            ),
    }
    generic_handler = grpc.method_handlers_generic_handler(
            'GrpcAdapter', rpc_method_handlers)
    server.add_generic_rpc_handlers((generic_handler,))


 # This class is part of an EXPERIMENTAL API.
class GrpcAdapter(object):
    """Missing associated documentation comment in .proto file."""

    @staticmethod
    def streamData(request_iterator,
            target,
            options=(),
            channel_credentials=None,
            call_credentials=None,
            insecure=False,
            compression=None,
            wait_for_ready=None,
            timeout=None,
            metadata=None):
        return grpc.experimental.stream_stream(request_iterator, target, '/GrpcAdapter/streamData',
            grpc__adpt__pb2.Request.SerializeToString,
            grpc__adpt__pb2.Response.FromString,
            options, channel_credentials,
            insecure, call_credentials, compression, wait_for_ready, timeout, metadata)