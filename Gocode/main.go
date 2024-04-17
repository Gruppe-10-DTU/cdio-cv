package main

import (
	pbuf "Gocode/proto"
	"github.com/ev3go/ev3dev"
	"google.golang.org/grpc"
	"google.golang.org/protobuf/proto"
	"log"
	"math"
	"net"
)

type robotServer struct {
	pbuf.UnimplementedRobotServer
}

const WHEEL_DIAMETER int = 40

const (
	RUN     = "RUN-forever"
	STOP    = "STOP"
	ABS_POS = "RUN-to-abs-pos"
	RESET   = "RESET"
)

func main() {
	lis, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}

	grpcServer := grpc.NewServer()

	pbuf.RegisterRobotServer(grpcServer, &robotServer{})
	err = grpcServer.Serve(lis)
	if err != nil {
		log.Fatalf("failed to serve: %v", err)
	}
}

func (grpcServer *robotServer) move(request *pbuf.MoveReq) error {

	leftMotor, err := ev3dev.TachoMotorFor("ev3-ports:outA", "lego-ev3-l-motor")
	if err != nil {
		log.Print(err)
		return err
	}
	rightMotor, err := ev3dev.TachoMotorFor("ev3-ports:outD", "lego-ev3-l-motor")
	if err != nil {
		log.Print(err)
		return err
	}
	leftMotor.Command(RESET)
	rightMotor.Command(RESET)

	direction := request.Direction
	distance := int(request.Distance)
	speed := int(request.Speed)

	switch direction {
	case "backward":
		speed *= -1
	case "forward":
		speed = speed
	default:
		return proto.Error
	}

	pos := 0

	leftMotor.SetSpeedSetpoint(speed)
	rightMotor.SetSpeedSetpoint(speed)

	leftMotor.Command(RUN)
	rightMotor.Command(RUN)
	for distance > pos {
		pos1, _ := leftMotor.Position()
		pos2, _ := rightMotor.Position()
		pos = int(math.Ceil(float64(pos1+pos2)/(360*2.0)) * (float64(WHEEL_DIAMETER) * 2 * math.Pi))
	}

	leftMotor.Command(STOP)
	rightMotor.Command(STOP)

	return nil
}

func (grpcServer *robotServer) turn(request *pbuf.TurnRequest) error {
	/* TODO */

	return nil
}

func (grpcServer *robotServer) vacuum(request *pbuf.VacuumPower) error {

	return nil
}

func (grpcServer *robotServer) stopMovement(request *pbuf.Empty) error {
	leftMotor, err := ev3dev.TachoMotorFor("ev3-ports:outA", "lego-ev3-l-motor")
	if err != nil {
		log.Print(err)
		return err
	}
	rightMotor, err := ev3dev.TachoMotorFor("ev3-ports:outD", "lego-ev3-l-motor")
	if err != nil {
		log.Print(err)
		return err
	}

	rightMotor.Command(STOP)
	leftMotor.Command(STOP)

	return nil
}

func (grpcServer *robotServer) stats(request *pbuf.Status) error {
	/* TODO */

	return nil
}
