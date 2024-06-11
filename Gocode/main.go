package main

import (
	peripherherals "Gocode/peripherals"
	pbuf "Gocode/proto"
	"fmt"
	"github.com/ev3go/ev3dev"
	"golang.org/x/net/context"
	"google.golang.org/grpc"
	"log"
	"math"
	"net"
	"time"
)

const WHEEL_DIAMETER float64 = 5.6
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
	//fmt.Printf("Received move command ... \n")
	leftMotor, err := peripherherals.GetMotor("left")
	if err != nil {
		errMsg := "Couldn't get reference for left motor"
		return &pbuf.Status{ErrCode: false, Message: &errMsg}, err
	}
	rightMotor, err := peripherherals.GetMotor("right")
	if err != nil {
		errMsg := "Couldn't get reference for right motor"
		return &pbuf.Status{ErrCode: false, Message: &errMsg}, err
	}
	if leftMotor == rightMotor {
		errMsg := "Motors are the same"
		return &pbuf.Status{ErrCode: false, Message: &errMsg}, nil
	}

	leftMotor.Command(RESET)
	rightMotor.Command(RESET)

	leftMotor.SetStopAction(BRAKE)
	rightMotor.SetStopAction(BRAKE)
	peripherherals.ResetGyros()

	direction := 0.0
	distance := int(request.Distance)
	speed := int(request.Speed)
	distance = int((float64(distance) / (WHEEL_DIAMETER * math.Pi)) * float64(leftMotor.CountPerRot()))
	switch request.Direction {
	case false:
		direction = -1.0
	case true:
		direction = 1.0
	default:
		return &pbuf.Status{ErrCode: false}, err
	}
	speed = speed * int(direction)
	Kp := float64(speed*speed) / 2000.0
	Ki := Kp * 0.1
	Kd := Kp * 0.5

	if request.Kp != nil {
		Kp = float64(*request.Kp)
	}
	if request.Ki != nil {
		Ki = float64(*request.Ki)
	}
	if request.Kd != nil {
		Kd = float64(*request.Kd)
	}

	integral, lastError := 0.0, 0.0
	target, gyroCount, gErr := peripherherals.GetGyroValue()
	if gyroCount == 0 || gErr != nil {
		rightMotor.Command(RESET)
		leftMotor.Command(RESET)
		errMsg := "Error reading target direction"
		return &pbuf.Status{ErrCode: false, Message: &errMsg}, gErr
	}
	pos := 0
	leftMotor.Command(DIR)
	rightMotor.Command(DIR)
	for distance > pos {
		deg, gyroCount, gErr := peripherherals.GetGyroValue()
		if gyroCount == 0 || gErr != nil {
			rightMotor.Command(RESET)
			leftMotor.Command(RESET)
			errMsg := "Error reading gyro values"
			return &pbuf.Status{ErrCode: false, Message: &errMsg}, gErr
		}
		gyroError := target - deg
		integral = math.Max(math.Min(integral+gyroError, 20.0), -20.0) // To handle saturation due to max speed of motor
		derivative := gyroError - lastError
		correction := (Kp * gyroError) + (Ki * integral) + (Kd * derivative)
		lastError = gyroError

		leftSp := math.Max(math.Min(float64(speed)+correction, 100.0), -100.0)  // To handle saturation due to max speed of motor
		rightSp := math.Max(math.Min(float64(speed)-correction, 100.0), -100.0) // To handle saturation due to max speed of motor

		leftMotor.SetDutyCycleSetpoint(int(leftSp))
		rightMotor.SetDutyCycleSetpoint(int(rightSp))

		time.Sleep(10 * time.Millisecond)

		if !peripherherals.BothMotorsRunning() {
			rightMotor.Command(RESET)
			leftMotor.Command(RESET)
			errMsg := "Both motors aren't running"
			return &pbuf.Status{ErrCode: false, Message: &errMsg}, nil
		}

		pos1, _ := leftMotor.Position()
		pos2, _ := rightMotor.Position()
		pos = int(math.Max(float64(pos1)*direction, float64(pos2)*direction))
		fmt.Printf("Heading: %f\tDistance: %d/%d\n", gyroError, pos, distance)
	}

	leftMotor.Command(STOP)
	rightMotor.Command(STOP)

	time.Sleep(5 * time.Millisecond)

	leftMotor.Command(RESET)
	rightMotor.Command(RESET)

	return &pbuf.Status{ErrCode: true}, nil
}

func (s *robotServer) Turn(_ context.Context, request *pbuf.TurnRequest) (*pbuf.Status, error) {
	leftMotor, err := peripherherals.GetMotor("left")
	if err != nil {
		errMsg := "Error getting left motor"
		return &pbuf.Status{ErrCode: false, Message: &errMsg}, err
	}

	rightMotor, err := peripherherals.GetMotor("right")
	if err != nil {
		errMsg := "Error getting right motor"
		return &pbuf.Status{ErrCode: false, Message: &errMsg}, err
	}
	if leftMotor == rightMotor {
		errMsg := "Only one motor available"
		return &pbuf.Status{ErrCode: false, Message: &errMsg}, nil
	}
	leftMotor.Command(RESET)
	rightMotor.Command(RESET)

	leftMotor.SetStopAction(BRAKE)
	rightMotor.SetStopAction(BRAKE)
	peripherherals.ResetGyros()

	direction := 0.0
	speed := 90.0
	var forwardMotor *ev3dev.TachoMotor
	var backwardMotor *ev3dev.TachoMotor
	if request.Degrees < 0 {
		direction = -1
		forwardMotor = rightMotor
		backwardMotor = leftMotor
	} else {
		direction = 1
		forwardMotor = leftMotor
		backwardMotor = rightMotor
	}
	degrees := float64(request.Degrees) * direction
	Kp := speed / 100.0
	Kd := Kp / 2.0
	power := 0
	pos := 0.0
	lastPos := 0.0

	forwardMotor.Command(DIR)
	backwardMotor.Command(DIR)

	for degrees > pos {
		dynSpeed := Kp*(degrees-pos) + Kd*(pos-lastPos)
		lastPos = pos
		if speed > dynSpeed {
			power = int(math.Max(dynSpeed, 40.0))
		} else {
			power = int(speed)
		}
		forwardMotor.SetDutyCycleSetpoint(power)
		backwardMotor.SetDutyCycleSetpoint(-power)
		time.Sleep(10 * time.Millisecond)
		if !peripherherals.BothMotorsRunning() {
			rightMotor.Command(RESET)
			leftMotor.Command(RESET)
			errMsg := "Both motors aren't running"
			return &pbuf.Status{ErrCode: false, Message: &errMsg}, err
		}

		gyroDeg, gyroCount, gErr := peripherherals.GetGyroValue()
		if gyroCount == 0 {
			rightMotor.Command(RESET)
			leftMotor.Command(RESET)
			errMsg := "Error reading gyro values"
			return &pbuf.Status{ErrCode: false, Message: &errMsg}, gErr
		}
		pos = gyroDeg * direction
		fmt.Printf("Heading: %f\n", gyroDeg)
	}
	leftMotor.Command(STOP)
	rightMotor.Command(STOP)

	time.Sleep(5 * time.Millisecond)

	leftMotor.Command(RESET)
	rightMotor.Command(RESET)
	return &pbuf.Status{ErrCode: true}, nil
}

func (s *robotServer) Vacuum(_ context.Context, request *pbuf.VacuumPower) (*pbuf.Status, error) {
	vacuumMotor, err := ev3dev.TachoMotorFor("ev3-ports:outB", "lego-ev3-m-motor")
	if err != nil {
		errMsg := "Error getting vacuum motor"
		return &pbuf.Status{ErrCode: false, Message: &errMsg}, err
	}
	vacuumMotor.Command(RESET)
	target := int(float32(vacuumMotor.CountPerRot()) * 0.95)
	vacuumMotor.SetSpeedSetpoint(800)
	if request.Power {
		target *= -1
	}
	vacuumMotor.SetPositionSetpoint(target)
	vacuumMotor.Command(ABS_POS)
	return &pbuf.Status{ErrCode: true}, err
}

func (s *robotServer) StopMovement(_ context.Context, request *pbuf.Empty) (*pbuf.Status, error) {
	rightMotor, err := ev3dev.TachoMotorFor("ev3-ports:outD", "lego-ev3-l-motor")
	if err != nil {
		errMsg := "Error getting left motor"
		return &pbuf.Status{ErrCode: false, Message: &errMsg}, err
	}
	leftMotor, err := ev3dev.TachoMotorFor("ev3-ports:outA", "lego-ev3-l-motor")
	if err != nil {
		errMsg := "Error getting right motor"
		return &pbuf.Status{ErrCode: false, Message: &errMsg}, err
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

func (s *robotServer) CelebrateVictory(_ context.Context, request *pbuf.Empty) (*pbuf.Status, error) {
	leftMotor, _ := peripherherals.GetMotor("left")
	rightMotor, _ := peripherherals.GetMotor("right")

	leftMotor.Command(RESET)
	rightMotor.Command(RESET)
	peripherherals.ResetGyros()
	wiggle := 100
	rotation := 360.0
	direction := 1.0
	cycles := 4
	leftMotor.Command(DIR)
	rightMotor.Command(DIR)
	for cycles > 0 {
		peripherherals.ResetGyros()
		i := 5
		for i > 0 {
			leftMotor.SetDutyCycleSetpoint(wiggle)
			rightMotor.SetDutyCycleSetpoint(-wiggle)
			wiggle *= -1
			i -= 1
			time.Sleep(250 * time.Millisecond)
		}
		peripherherals.ResetGyros()
		deg, _, _ := peripherherals.GetGyroValue()
		for deg*direction < rotation {
			speed := 100 * int(direction)
			leftMotor.SetDutyCycleSetpoint(speed)
			rightMotor.SetDutyCycleSetpoint(-speed)
			deg, _, _ = peripherherals.GetGyroValue()
			time.Sleep(5 * time.Millisecond)
		}
		direction *= -1
		cycles -= 1
	}
	leftMotor.Command(RESET)
	rightMotor.Command(RESET)
	msg := "What"
	return &pbuf.Status{ErrCode: true, Message: &msg}, nil
}
