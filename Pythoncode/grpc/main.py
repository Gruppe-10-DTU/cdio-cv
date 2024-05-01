import grpc

import protobuf_pb2
import protobuf_pb2_grpc

def run():
    with grpc.insecure_channel("172.20.10.12:50051") as channel:
        stub = protobuf_pb2_grpc.RobotStub(channel)
        stub.Turn(protobuf_pb2.TurnRequest(degrees=-10))
    print("Move forward request sent")

if __name__ == "__main__":
    run()