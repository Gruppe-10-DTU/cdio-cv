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
var gyro1 *ev3dev.Sensor
var gyro2 *ev3dev.Sensor

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

	direction := 0.0
	distance := int(request.Distance)
	speed := int(request.Speed)
	distance = int(float32(distance) / (float32(WHEEL_DIAMETER) * 2 * math.Pi))
	switch request.Direction {
	case "backward":
		direction = -1.0
	case "forward":
		direction = 1.0
	default:
		return proto.Error
	}
	speed = speed * int(direction)
	Kp := 0.0
	Ki := 0.0
	Kd := 0.0
	gyroError := 0.0
	integral := 0.0
	derivative := 0.0
	lastError := 0.0
	correction := 0.0
	target := 0.0
	pos := 0
	for distance > pos {
		gyroError = target - getGyroValue()
		integral = integral + gyroError
		derivative = gyroError - lastError
		correction = ((Kp * gyroError) + (Ki * integral) + (Kd * derivative)) * direction

		leftMotor.SetSpeedSetpoint(speed + int(correction))
		rightMotor.SetSpeedSetpoint(speed - int(correction))

		leftMotor.Command(RUN)
		rightMotor.Command(RUN)

		pos1, _ := leftMotor.Position()
		pos2, _ := rightMotor.Position()
		pos = (pos1 + pos2) / 2
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
	var forwardMotor *ev3dev.TachoMotor
	var backwardMotor *ev3dev.TachoMotor
	switch request.Direction {
	case "left":
		direction = -1.0
		forwardMotor = rightMotor
		backwardMotor = leftMotor
	case "right":
		direction = 1.0
		forwardMotor = rightMotor
		backwardMotor = leftMotor
	default:
		return proto.Error
	}

	Kp := speed / 10
	power := speed
	pos := 0
	for degrees > pos {
		if speed > Kp*(degrees-pos) {
			power = (degrees - pos) * Kp
		} else {
			power = speed
		}
		forwardMotor.SetSpeedSetpoint(power)
		backwardMotor.SetSpeedSetpoint(-power)

		forwardMotor.Command(RUN)
		backwardMotor.Command(RUN)

		pos = int(math.Ceil(getGyroValue() * direction))
	}
	leftMotor.Command(STOP)
	rightMotor.Command(STOP)
	return nil
}

func (grpcServer *robotServer) vacuum(request *pbuf.VacuumPower) error {
	vacuumMotor.Command(RESET)
	target := int(float32(vacuumMotor.CountPerRot()) * 1.25)
	vacuumMotor.SetSpeedSetpoint(500)
	if !request.Power {
		target *= -1
	}
	vacuumMotor.SetPositionSetpoint(target)
	vacuumMotor.Command(ABS_POS)
	return nil
}

func (grpcServer *robotServer) stopMovement(request *pbuf.Empty) error {
	rightMotor.Command(RESET)
	leftMotor.Command(RESET)
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

	gyro1, err = ev3dev.SensorFor("ev3-ports:in1", "lego-ev3-gyro")
	if err != nil {
		log.Fatal(err)
	}

	gyro2, err = ev3dev.SensorFor("ev3-ports:in1", "lego-ev3-gyro")
	if err != nil {
		log.Fatal(err)
	}
}
func getGyroValue() float64 {

	tmp, _ := gyro1.Value(math.MaxInt)
	pos1, _ := strconv.ParseFloat(tmp, 32)
	tmp, _ = gyro2.Value(math.MaxInt)
	pos2, _ := strconv.ParseFloat(tmp, 32)

	return (pos1 + pos2) / 2.0
}
func resetGyros() {
	gyro1.SetMode("GYRO-CAL")
	gyro1.SetMode("GYRO-ANG")

	gyro2.SetMode("GYRO-CAL")
	gyro2.SetMode("GYRO-ANG")
}
