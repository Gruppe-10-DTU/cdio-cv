import grpc

import protobuf_pb2
import protobuf_pb2_grpc

def run():
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = protobuf_pb2_grpc.RobotStub(channel)
        stub.move(protobuf_pb2.MoveReq("1", 2, 3))
    print("Move forward request sent")

if __name__ == "__main__":
    run()