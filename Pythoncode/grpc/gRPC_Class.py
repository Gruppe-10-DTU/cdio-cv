import grpc

from Pythoncode.grpc import protobuf_pb2_grpc, protobuf_pb2


class gRPC_Class:
    def __init__(self):
        print("grpc started")

    def move(self, distance: int):
        with grpc.insecure_channel("172.20.10.12:50051") as channel:
            stub = protobuf_pb2_grpc.RobotStub(channel)
            stub.Move(protobuf_pb2.MoveRequest(direction=True, distance=200, speed=300))
