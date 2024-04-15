package main

import (
	pbuf "Gocode/proto"
	"github.com/ev3go/ev3dev"
	"google.golang.org/grpc"
	"google.golang.org/protobuf/proto"
	"log"
	"math"
	"net"
	"strconv"
	"time"
)

type robotServer struct {
	pbuf.UnimplementedRobotServer
}

const WHEEL_DIAMETER int = 40

const (
	RUN     = "run-forever"
	STOP    = "stop"
	ABS_POS = "run-to-abs-pos"
	RESET   = "reset"
)

var leftMotor *ev3dev.TachoMotor
var rightMotor *ev3dev.TachoMotor
var vacuumMotor *ev3dev.TachoMotor
var gyro_1 *ev3dev.Sensor
var gyro_2 *ev3dev.Sensor

func main() {

	initializeRobotPeripherals()

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
		pos = int(math.Ceil(((float64(pos1/leftMotor.CountPerRot()) + float64(pos2/rightMotor.CountPerRot())) / 2.0) * (float64(WHEEL_DIAMETER) * 2 * math.Pi)))
	}

	leftMotor.Command(STOP)
	rightMotor.Command(STOP)

	return nil
}

func (grpcServer *robotServer) turn(request *pbuf.TurnRequest) error {

	resetGyros()

	degrees := int(request.Degrees)
	direction := 1.0
	speed := 500
	switch request.Direction {
	case "left":
		direction = -1.0
	case "right":
		direction = 1.0
	default:
		return proto.Error
	}
	leftMotor.SetSpeedSetpoint(speed)
	leftMotor.SetRampUpSetpoint(2 * time.Second)

	rightMotor.SetSpeedSetpoint(speed)
	rightMotor.SetRampUpSetpoint(2 * time.Second)
	pos := 0
	for degrees > pos {
		leftMotor.Command(RUN)
		rightMotor.Command(RUN)

		pos = int(math.Ceil(getGyroValue() * direction))
	}

	return nil
}

func (grpcServer *robotServer) vacuum(request *pbuf.VacuumPower) error {

	return nil
}

func (grpcServer *robotServer) stopMovement(request *pbuf.Empty) error {

	rightMotor.Command(STOP)
	leftMotor.Command(STOP)

	return nil
}

func (grpcServer *robotServer) stats(request *pbuf.Status) error {
	/* TODO */

	return nil
}

func initializeRobotPeripherals() {
	var err error
	leftMotor, err = ev3dev.TachoMotorFor("ev3-ports:outA", "lego-ev3-l-motor")
	if err != nil {
		log.Fatal(err)
	}
	rightMotor, err = ev3dev.TachoMotorFor("ev3-ports:outD", "lego-ev3-l-motor")
	if err != nil {
		log.Fatal(err)
	}

	vacuumMotor, err = ev3dev.TachoMotorFor("ev3-ports:outD", "lego-ev3-l-motor")
	if err != nil {
		log.Fatal(err)
	}

	gyro_1, err = ev3dev.SensorFor("ev3-ports:in1", "lego-ev3-gyro")
	if err != nil {
		log.Fatal(err)
	}

	gyro_2, err = ev3dev.SensorFor("ev3-ports:in1", "lego-ev3-gyro")
	if err != nil {
		log.Fatal(err)
	}
}
func getGyroValue() float64 {

	tmp, _ := gyro_1.Value(math.MaxInt)
	pos1, _ := strconv.ParseFloat(tmp, 64)
	tmp, _ = gyro_2.Value(math.MaxInt)
	pos2, _ := strconv.ParseFloat(tmp, 64)

	return (pos1 + pos2) / 2.0
}
func resetGyros() {
	gyro_1.SetMode("GYRO-CAL")
	gyro_1.SetMode("GYRO-ANG")

	gyro_2.SetMode("GYRO-CAL")
	gyro_2.SetMode("GYRO-ANG")
}
