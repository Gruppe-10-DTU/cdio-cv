package main

import (
	pbuf "Gocode/proto"
	"flag"
	"google.golang.org/grpc"
	"log"
	"net"
)

type robotServer struct {
	pbuf.UnimplementedRobotServer
}

func main() {
	flag.Parse()
	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Printf("failed to listen: %v", err)
	}

	grpcServer := grpc.NewServer()

	pbuf.RegisterRobotServer(grpcServer, &robotServer{})
	err = grpcServer.Serve(lis)
	if err != nil {
		log.Printf("failed to serve: %v", err)
	}
}

func (grpcServer *robotServer) move(request pbuf.MoveReq) error {
	/* TODO */

	return nil
}

func (grpcServer *robotServer) turn(request pbuf.TurnRequest) error {
	/* TODO */

	return nil
}

func (grpcServer *robotServer) vacuum(request pbuf.VacuumPower) error {

	return nil
}

func (grpcServer *robotServer) stopMovement(request pbuf.Empty) error {
	/* TODO */

	return nil
}

func (grpcServer *robotServer) stats(request pbuf.Status) error {
	/* TODO */

	return nil
}
