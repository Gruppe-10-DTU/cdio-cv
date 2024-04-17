import grpc

from Pythoncode.grpc import protobuf_pb2_grpc, protobuf_pb2


class gRPC:
    def __init__(self):
        print("grpc started")


    def move(self):
        with grpc.insecure_channel("172.20.10.12:50051") as channel:
            stub = protobuf_pb2_grpc.RobotStub(channel)
            stub.move(protobuf_pb2.MoveReq(direction="1", distance=2, speed=3))
        print("Move forward request sent")
