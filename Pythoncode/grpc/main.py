import grpc

import protobuf_pb2
import protobuf_pb2_grpc

def run():
    # Go forward testing
    with grpc.insecure_channel("localhost:50051") as channel:
        stub = protobuf_pb2_grpc.RobotStub(channel)
        response = stub.Move(protobuf_pb2.MoveRequest(direction="1", distance=2, speed=3))
        print(response)

if __name__ == "__main__":
    run()