import grpc
import time

import protobuf_pb2
import protobuf_pb2_grpc


def run():

    with grpc.insecure_channel("localhost:50051") as channel:
        stub = protobuf_pb2_grpc.RobotStub(channel)

        # Go forward testing
        response = stub.Move(protobuf_pb2.MoveRequest(direction="1", distance=2, speed=3))
        print(response)

        time.sleep(3)

        # backwards
        response = stub.Move(protobuf_pb2.MoveRequest(direction="-1", distance=2, speed=3))
        print(response)

        time.sleep(3)

        # Turn
        response = stub.Turn(protobuf_pb2.TurnRequest(direction="1", degrees=2))
        print(response)


if __name__ == "__main__":
    run()
