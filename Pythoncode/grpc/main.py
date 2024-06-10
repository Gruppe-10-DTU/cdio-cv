import configparser

import grpc

import protobuf_pb2
import protobuf_pb2_grpc

def run():
    config = configparser.ConfigParser()
    config.read('properties/config.ini')
    ip = config.get("ROBOT", "ip")
    with grpc.insecure_channel(ip) as channel:
        stub = protobuf_pb2_grpc.RobotStub(channel)
        stub.StopMovement(protobuf_pb2.Empty())
        stub.Turn(protobuf_pb2.TurnRequest(degrees=-90))

if __name__ == "__main__":
    run()