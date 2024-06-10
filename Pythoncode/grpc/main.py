import grpc

import protobuf_pb2
import protobuf_pb2_grpc

def run():
    with grpc.insecure_channel("192.168.53.19:50051") as channel:
        stub = protobuf_pb2_grpc.RobotStub(channel)
        stub.StopMovement(protobuf_pb2.Empty())
        stub.Turn(protobuf_pb2.TurnRequest(degrees=-90))

        """


        """


    print("Move forward request sent")

if __name__ == "__main__":
    run()