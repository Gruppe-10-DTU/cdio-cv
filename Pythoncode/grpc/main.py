import configparser
from time import sleep

import grpc

import protobuf_pb2
import protobuf_pb2_grpc

def run():
    config = configparser.ConfigParser()
    config.read('../config.ini')
    ip = config.get("ROBOT", "ip")
    with grpc.insecure_channel(ip) as channel:
        stub = protobuf_pb2_grpc.RobotStub(channel)
        stub.StopMovement(protobuf_pb2.Empty())
        """ stub.Move(protobuf_pb2.MoveRequest(direction=False,distance=1,speed=30))
            stub.Move(protobuf_pb2.MoveRequest(direction=True,distance=1,speed=30))
            
        """
        while True:
            stub.Vacuum(protobuf_pb2.VacuumPower(power=False))
            sleep(4)
            stub.Vacuum(protobuf_pb2.VacuumPower(power=True))
            sleep(5)





if __name__ == "__main__":
    run()