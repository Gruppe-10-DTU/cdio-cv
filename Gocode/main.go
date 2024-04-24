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
	"time"
)

const WHEEL_DIAMETER float32 = 5.6
const (
	RUN     = "run-forever"
	DIR     = "run-direct"
	STOP    = "stop"
	ABS_POS = "run-to-abs-pos"
	REL_POS = "run-to-rel-pos"
	TIME    = "run-timed"
	RESET   = "reset"

	BRAKE = "brake"
	COAST = "coast"
	HOLD  = "hold"
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
	leftMotor, err := ev3dev.TachoMotorFor("ev3-ports:outA", "lego-ev3-l-motor")
	if err != nil {
		return &pbuf.Status{ErrCode: false}, err
	}
	rightMotor, err := ev3dev.TachoMotorFor("ev3-ports:outD", "lego-ev3-l-motor")
	if err != nil {
		return &pbuf.Status{ErrCode: false}, err
	}

	leftMotor.Command(RESET)
	rightMotor.Command(RESET)

	leftMotor.SetStopAction(BRAKE)
	rightMotor.SetStopAction(BRAKE)
	resetGyros()

	direction := 0.0
	distance := int(request.Distance)
	speed := int(request.Speed)
	distance = int(float32(distance)/(float32(WHEEL_DIAMETER)*math.Pi)) * leftMotor.CountPerRot()
	switch request.Direction {
	case []byte{0}:
		direction = -1.0
	case []byte{1}:
		direction = 1.0
	default:
		return &pbuf.Status{ErrCode: false}, err
	}
	speed = speed * int(direction)
	Kp := float64(speed*speed) / 20000.0
	Ki := Kp * 0.1
	Kd := Kp * 0.5
	switch {
	case request.Kp != nil:
		Kp = float64(*request.Kp)
	case request.Ki != nil:
		Ki = float64(*request.Ki)
	case request.Kd != nil:
		Kd = float64(*request.Kd)
	}

	integral, lastError := 0.0, 0.0
	target, _ := getGyroValue()
	pos := 0
	for distance > pos {
		deg, _ := getGyroValue()
		gyroError := target - deg
		integral = math.Max(math.Min(integral+gyroError, 500.0), -500.0) // To handle saturation due to max speed of motor
		derivative := gyroError - lastError
		correction := (Kp * gyroError) + (Ki * integral) + (Kd * derivative)
		lastError = gyroError

		leftMotor.SetRampUpSetpoint(100 * time.Millisecond)
		rightMotor.SetRampUpSetpoint(100 * time.Millisecond)

		leftMotor.SetRampDownSetpoint(100 * time.Millisecond)
		rightMotor.SetRampDownSetpoint(100 * time.Millisecond)

		leftMotor.SetSpeedSetpoint(speed + int(correction))
		rightMotor.SetSpeedSetpoint(speed - int(correction))

		leftMotor.Command(RUN)
		rightMotor.Command(RUN)

		pos1, _ := leftMotor.Position()
		pos2, _ := rightMotor.Position()
		pos = int(math.Max(float64(pos1)*direction, float64(pos2)*direction))
		//fmt.Printf("Status:\tHeading: %f\tcorrection: %f\tIntegral: %f\n", deg, correction, integral)
	}

	leftMotor.Command(STOP)
	rightMotor.Command(STOP)

	return &pbuf.Status{ErrCode: true}, nil
}

func (s *robotServer) Turn(_ context.Context, request *pbuf.TurnRequest) (*pbuf.Status, error) {
	fmt.Printf("Received turn command ... \n")
	leftMotor, err := ev3dev.TachoMotorFor("ev3-ports:outA", "lego-ev3-l-motor")
	if err != nil {
		return &pbuf.Status{ErrCode: false}, err
	}

	rightMotor, err := ev3dev.TachoMotorFor("ev3-ports:outD", "lego-ev3-l-motor")
	if err != nil {
		return &pbuf.Status{ErrCode: false}, err
	}

	resetGyros()

	degrees := int(request.Degrees)
	direction := 0.0
	speed := 500
	var forwardMotor *ev3dev.TachoMotor
	var backwardMotor *ev3dev.TachoMotor
	switch request.Degrees < 0 {
	case true:
		direction = -1.0
		forwardMotor = rightMotor
		backwardMotor = leftMotor
	case false:
		direction = 1.0
		forwardMotor = leftMotor
		backwardMotor = rightMotor
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
		//fmt.Printf("Heading: %f\n", deg)
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
	rightMotor, err := ev3dev.TachoMotorFor("ev3-ports:outD", "lego-ev3-l-motor")
	if err != nil {
		return &pbuf.Status{ErrCode: false}, err
	}
	leftMotor, err := ev3dev.TachoMotorFor("ev3-ports:outA", "lego-ev3-l-motor")
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
	gyro2, err := ev3dev.SensorFor("ev3-ports:in4", "lego-ev3-gyro")
	if err != nil {
		return
	}
	gyro1.SetMode("GYRO-ANG")
	gyro2.SetMode("GYRO-ANG")

	direct, err := gyro1.Direct(777)
	if err != nil {
		fmt.Printf("Gyro 1 open: %s\n", err)
		return
	}
	_, err = direct.Write([]byte("\x88"))
	if err != nil {
		fmt.Printf("Gyro 1 write: %s\n", err)
		return
	}
	err = direct.Close()
	if err != nil {
		fmt.Printf("Gyro 1 close: %s\n", err)
		return
	}
	direct, err = gyro2.Direct(666)
	if err != nil {
		fmt.Printf("Gyro 2 open: %s\n", err)
		return
	}
	_, err = direct.Write([]byte("\x88"))
	if err != nil {
		fmt.Printf("Gyro 2 write: %s\n", err)
		return
	}
	err = direct.Close()
	if err != nil {
		fmt.Printf("Gyro 2 close: %s\n", err)
		return
	}
	//time.Sleep(250 * time.Millisecond)

	gyro1.SetPollRate(5 * time.Millisecond)
	gyro2.SetPollRate(5 * time.Millisecond)

}
