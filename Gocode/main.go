package main

import (
	pbuf "Gocode/proto"
	"fmt"
	"github.com/ev3go/ev3dev"
	"golang.org/x/net/context"
	"google.golang.org/grpc"
	"google.golang.org/protobuf/proto"
	"log"
	"math"
	"net"
	"strconv"
)

const WHEEL_DIAMETER float32 = 5.6
const (
	RUN     = "run-forever"
	STOP    = "stop"
	ABS_POS = "run-to-abs-pos"
	RESET   = "reset"
)

type robotServer struct {
	pbuf.UnimplementedRobotServer
}

func main() {

	//initializeRobotPeripherals()

	listen, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	fmt.Printf("Succesful bind on 50051 ...\n")
	server := grpc.NewServer()
	fmt.Printf("Created robotServer ...\n")
	pbuf.RegisterRobotServer(server, &robotServer{})
	fmt.Printf("Registered robotServer ...\n")
	err = server.Serve(listen)
	if err != nil {
		log.Fatalf("failed to serve: %v", err)
	}

}

func (s *robotServer) Move(_ context.Context, request *pbuf.MoveRequest) (*pbuf.Status, error) {
	fmt.Printf("Received move command ... \n")
	rightMotor, err := ev3dev.TachoMotorFor("ev3-ports:outA", "lego-ev3-l-motor")
	if err != nil {
		return &pbuf.Status{ErrCode: false}, err
	}
	leftMotor, err := ev3dev.TachoMotorFor("ev3-ports:outD", "lego-ev3-l-motor")
	if err != nil {
		return &pbuf.Status{ErrCode: false}, err
	}

	leftMotor.Command(RESET)
	rightMotor.Command(RESET)

	direction := 0.0
	distance := int(request.Distance)
	speed := int(request.Speed)
	distance = int(float32(distance)/(float32(WHEEL_DIAMETER)*math.Pi)) * leftMotor.CountPerRot()
	switch request.Direction {
	case "backward":
		direction = -1.0
	case "forward":
		direction = 1.0
	default:
		return &pbuf.Status{ErrCode: false}, err
	}
	speed = speed * int(direction)
	Kp := 10.0
	Ki := 1.0
	Kd := 5.0
	switch {
	case request.Kp != nil:
		Kp = float64(*request.Kp)
	case request.Ki != nil:
		Ki = float64(*request.Ki)
	case request.Kd != nil:
		Kd = float64(*request.Kd)
	}
	gyroError := 0.0
	integral := 0.0
	derivative := 0.0
	lastError := 0.0
	correction := 0.0
	target := 0.0
	pos := 0
	for distance > pos {
		deg, _ := getGyroValue()
		fmt.Printf("heading: %f \n", deg)
		gyroError = target - deg
		integral = integral + gyroError
		derivative = gyroError - lastError
		correction = ((Kp * gyroError) + (Ki * integral) + (Kd * derivative)) * direction

		leftMotor.SetSpeedSetpoint(speed - int(correction))
		rightMotor.SetSpeedSetpoint(speed + int(correction))

		leftMotor.Command(RUN)
		rightMotor.Command(RUN)

		pos1, _ := leftMotor.Position()
		pos2, _ := rightMotor.Position()
		pos = (pos1 + pos2) / 2
	}

	leftMotor.Command(STOP)
	rightMotor.Command(STOP)

	return &pbuf.Status{ErrCode: true}, nil
}

func (s *robotServer) Turn(_ context.Context, request *pbuf.TurnRequest) (*pbuf.Status, error) {
	fmt.Printf("Received turn command ... \n")
	rightMotor, err := ev3dev.TachoMotorFor("ev3-ports:outA", "lego-ev3-l-motor")
	if err != nil {
		return &pbuf.Status{ErrCode: false}, err
	}
	leftMotor, err := ev3dev.TachoMotorFor("ev3-ports:outD", "lego-ev3-l-motor")
	if err != nil {
		return &pbuf.Status{ErrCode: false}, err
	}
	resetGyros()

	degrees := int(request.Degrees)
	direction := 0.0
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
		return &pbuf.Status{ErrCode: false}, proto.Error
	}

	Kp := speed / 10
	power := 0
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
		deg, _ := getGyroValue()
		pos = int(math.Ceil(deg * direction))
	}
	leftMotor.Command(STOP)
	rightMotor.Command(STOP)
	return &pbuf.Status{ErrCode: true}, nil
}

func (s *robotServer) Vacuum(_ context.Context, request *pbuf.VacuumPower) (*pbuf.Status, error) {
	vacuumMotor, err := ev3dev.TachoMotorFor("ev3-ports:outB", "lego-ev3-l-motor")
	if err != nil {
		return &pbuf.Status{ErrCode: false}, err
	}
	vacuumMotor.Command(RESET)
	target := int(float32(vacuumMotor.CountPerRot()) * 1.25)
	vacuumMotor.SetSpeedSetpoint(500)
	if !request.Power {
		target *= -1
	}
	vacuumMotor.SetPositionSetpoint(target)
	vacuumMotor.Command(ABS_POS)
	return &pbuf.Status{ErrCode: true}, err
}

func (s *robotServer) StopMovement(_ context.Context, request *pbuf.Empty) (*pbuf.Status, error) {
	rightMotor, err := ev3dev.TachoMotorFor("ev3-ports:outA", "lego-ev3-l-motor")
	if err != nil {
		return &pbuf.Status{ErrCode: false}, err
	}
	leftMotor, err := ev3dev.TachoMotorFor("ev3-ports:outD", "lego-ev3-l-motor")
	if err != nil {
		return &pbuf.Status{ErrCode: false}, err
	}
	rightMotor.Command(RESET)
	leftMotor.Command(RESET)
	rightMotor.Command(STOP)
	leftMotor.Command(STOP)

	return &pbuf.Status{ErrCode: true}, nil
}

func (s *robotServer) Stats(_ context.Context, request *pbuf.Status) (*pbuf.Status, error) {
	/* TODO */

	return &pbuf.Status{ErrCode: true}, nil
}

func getGyroValue() (float64, error) {
	gyro1, err := ev3dev.SensorFor("ev3-ports:in1", "lego-ev3-gyro")
	if err != nil {
		return 0, err
	}
	gyro2, err := ev3dev.SensorFor("ev3-ports:in4", "lego-ev3-gyro")
	if err != nil {
		return 0, err
	}
	tmp, _ := gyro1.Value(0)
	pos1, _ := strconv.ParseFloat(tmp, 32)
	tmp, _ = gyro2.Value(0)
	pos2, _ := strconv.ParseFloat(tmp, 32)

	return (pos1 + pos2) / 2.0, nil
}
func resetGyros() {
	gyro1, err := ev3dev.SensorFor("ev3-ports:in1", "lego-ev3-gyro")
	if err != nil {
		return
	}
	gyro2, err := ev3dev.SensorFor("ev3-ports:in1", "lego-ev3-gyro")
	if err != nil {
		return
	}
	gyro1.SetMode("GYRO-CAL")
	gyro1.SetMode("GYRO-ANG")

	gyro2.SetMode("GYRO-CAL")
	gyro2.SetMode("GYRO-ANG")
}
