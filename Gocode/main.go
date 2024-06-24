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
	"strconv"
	"time"
)

const WheelDiameter float64 = 5.6
const RobotWidth float64 = 17.5
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

var vacuumIsOn bool

func main() {

	//initializeRobotPeripherals()
	vacuumIsOn = false
	listen, err := net.Listen("tcp", ":50051")
	if err != nil {
		log.Fatalf("failed to listen: %v", err)
	}
	fmt.Printf("Succesful bind on 50051 ...\n")
	server := grpc.NewServer()
	fmt.Printf("Created robotServer ...\n")
	pbuf.RegisterRobotServer(server, &robotServer{})
	fmt.Printf("Registered robotServer ...\n\n")
	err = server.Serve(listen)
	if err != nil {
		log.Fatalf("failed to serve: %v", err)
	}

}

func (s *robotServer) Move(_ context.Context, request *pbuf.MoveRequest) (*pbuf.Status, error) {
	//fmt.Printf("Received move command ... \n")
	leftMotor, err := peripherherals.GetMotor("left")
	if err != nil {
		errMsg := "Move failed: Couldn't get reference for left motor\n"
		fmt.Printf("%s", errMsg)
		return &pbuf.Status{ErrCode: false, Message: &errMsg}, err
	}
	rightMotor, err := peripherherals.GetMotor("right")
	if err != nil {
		errMsg := "Move failed: Couldn't get reference for right motor\n"
		fmt.Printf("%s", errMsg)
		return &pbuf.Status{ErrCode: false, Message: &errMsg}, err
	}
	if leftMotor == rightMotor {
		errMsg := "Move failed: Motors are the same\n"
		fmt.Printf("%s", errMsg)
		return &pbuf.Status{ErrCode: false, Message: &errMsg}, nil
	}

	leftMotor.Command(RESET)
	rightMotor.Command(RESET)

	leftMotor.SetStopAction(HOLD)
	rightMotor.SetStopAction(HOLD)
	peripherherals.ResetGyros()

	direction := 0.0
	distance := int(request.Distance)
	speed := int(request.Speed)
	distance = int((float64(distance) / (WheelDiameter * math.Pi)) * float64(leftMotor.CountPerRot()))
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
		errMsg := "Move failed: Error reading target direction"
		fmt.Printf("%s", errMsg)
		return &pbuf.Status{ErrCode: false, Message: &errMsg}, gErr
	}
	pos := 0
	leftMotor.Command(DIR)
	rightMotor.Command(DIR)
	leftMotor.SetPositionSetpoint(distance)
	rightMotor.SetPositionSetpoint(distance)
	for distance > pos {
		deg, gyroCount, gErr := peripherherals.GetGyroValue()
		if gyroCount == 0 || gErr != nil {
			rightState, _ := rightMotor.State()
			leftState, _ := leftMotor.State()
			errMsg := "Move failed: Both motors aren't running" +
				"\n\tRight state: " + rightState.String() + "\tLeft state:" + leftState.String() +
				"\n\tDistance: " + strconv.Itoa(pos) + "/" + strconv.Itoa(distance) + "\n"
			fmt.Printf("%s", errMsg)
			rightMotor.Command(STOP)
			leftMotor.Command(STOP)
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
			rightState, _ := rightMotor.State()
			leftState, _ := leftMotor.State()
			errMsg := "Move failed: Both motors aren't running" +
				"\n\tRight state: " + rightState.String() + "\tLeft state:" + leftState.String() +
				"\n\tDistance: " + strconv.Itoa(pos) + "/" + strconv.Itoa(distance) + "\n"
			fmt.Printf("%s", errMsg)
			rightMotor.Command(STOP)
			leftMotor.Command(STOP)
			return &pbuf.Status{ErrCode: false, Message: &errMsg}, nil
		}

		pos1, _ := leftMotor.Position()
		pos2, _ := rightMotor.Position()
		pos = int(math.Max(float64(pos1)*direction, float64(pos2)*direction))
	}

	leftMotor.Command(STOP)
	rightMotor.Command(STOP)

	time.Sleep(50 * time.Millisecond)

	leftMotor.Command(STOP)
	rightMotor.Command(STOP)
	return &pbuf.Status{ErrCode: true}, nil
}

func (s *robotServer) Turn(_ context.Context, request *pbuf.TurnRequest) (*pbuf.Status, error) {
	if math.Abs(float64(request.Degrees)) <= 15.0 {
		return precisionTurn(request)
	}
	leftMotor, err := peripherherals.GetMotor("left")
	if err != nil {
		errMsg := "Turn failed: Error getting left motor\n"
		fmt.Printf("%s", errMsg)
		return &pbuf.Status{ErrCode: false, Message: &errMsg}, err
	}

	rightMotor, err := peripherherals.GetMotor("right")
	if err != nil {
		errMsg := "Turn failed: Error getting right motor\n"
		fmt.Printf("%s", errMsg)
		return &pbuf.Status{ErrCode: false, Message: &errMsg}, err
	}
	if leftMotor == rightMotor {
		errMsg := "Turn failed: Only one motor available\n"
		fmt.Printf("%s", errMsg)
		return &pbuf.Status{ErrCode: false, Message: &errMsg}, nil
	}
	leftMotor.Command(RESET)
	rightMotor.Command(RESET)

	leftMotor.SetStopAction(BRAKE)
	rightMotor.SetStopAction(BRAKE)
	peripherherals.ResetGyros()

	direction := 0.0
	speed := 0.0
	if request.Speed != nil {
		speed = float64(*request.Speed)
	} else {
		speed = 80.0
	}
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
	overshot := false
	oscillationCount := 3
	for math.Abs(degrees-pos) > 1.0 || oscillationCount > 0 {
		if degrees < pos {
			overshot = true
		} else {
			overshot = false
		}
		dynSpeed := Kp*(degrees-pos) + Kd*(pos-lastPos)
		lastPos = pos
		if speed > dynSpeed {
			power = int(math.Max(dynSpeed, 40.0))
		} else {
			power = int(speed)
		}
		if overshot {
			power *= -1
		}
		if oscillationCount > 2 {
			forwardMotor.SetDutyCycleSetpoint(power)
			backwardMotor.SetDutyCycleSetpoint(-power)
		} else {
			forwardMotor.SetDutyCycleSetpoint(power)
			backwardMotor.Command(STOP)
		}
		time.Sleep(10 * time.Millisecond)
		if !peripherherals.BothMotorsRunning() && oscillationCount > 2 {
			rightState, _ := rightMotor.State()
			leftState, _ := leftMotor.State()
			errMsg := "Turn failed: Both motors aren't running" +
				"\n\tRight state: " + rightState.String() + "\tLeft state:" + leftState.String() +
				"\n\tAngle: " + strconv.FormatFloat(pos, 'g', -1, 32) + "/" + strconv.FormatFloat(degrees, 'g', -1, 32) + "\n"
			fmt.Printf("%s", errMsg)
			rightMotor.Command(STOP)
			leftMotor.Command(STOP)
			return &pbuf.Status{ErrCode: false, Message: &errMsg}, err
		}

		gyroDeg, gyroCount, gErr := peripherherals.GetGyroValue()
		if gyroCount == 0 {
			rightState, _ := rightMotor.State()
			leftState, _ := leftMotor.State()
			errMsg := "Turn failed: Error reading gyro" +
				"\n\tRight state: " + rightState.String() + "\tLeft state:" + leftState.String() +
				"\n\tAngle: " + strconv.FormatFloat(pos, 'g', -1, 32) + "/" + strconv.FormatFloat(degrees, 'g', -1, 32) + "\n"
			fmt.Printf("%s", errMsg)
			rightMotor.Command(STOP)
			leftMotor.Command(STOP)
			return &pbuf.Status{ErrCode: false}, gErr
		}
		pos = gyroDeg * direction
		if math.Abs(degrees-pos) < 1.5 {
			oscillationCount -= 1
		}
	}
	leftMotor.Command(STOP)
	rightMotor.Command(STOP)

	time.Sleep(5 * time.Millisecond)

	leftMotor.Command(STOP)
	rightMotor.Command(STOP)
	return &pbuf.Status{ErrCode: true}, nil
}

func (s *robotServer) Vacuum(_ context.Context, request *pbuf.VacuumPower) (*pbuf.Status, error) {
	if request.Power == vacuumIsOn {
		return &pbuf.Status{ErrCode: true}, nil
	}
	vacuumMotor, err := ev3dev.TachoMotorFor("ev3-ports:outB", "lego-ev3-m-motor")
	if err != nil {
		errMsg := "Error getting vacuum motor"
		fmt.Printf("Vacuum error: %s\n\tVacuum Running: %s\n", errMsg, strconv.FormatBool(vacuumIsOn))
		return &pbuf.Status{ErrCode: false, Message: &errMsg}, err
	}
	vacuumMotor.Command(RESET)
	vacuumMotor.SetStopAction(HOLD)
	target := 20
	vacuumMotor.SetSpeedSetpoint(vacuumMotor.MaxSpeed())
	if request.Power {
		target *= -1
	}
	vacuumMotor.SetPositionSetpoint(target)
	vacuumMotor.Command(REL_POS)
	vacuumIsOn = request.Power
	return &pbuf.Status{ErrCode: true}, err
}

func (s *robotServer) StopMovement(_ context.Context, _ *pbuf.Empty) (*pbuf.Status, error) {
	rightMotor, err := ev3dev.TachoMotorFor("ev3-ports:outD", "lego-ev3-l-motor")
	if err != nil {
		errMsg := "Error getting left motor"
		fmt.Printf("Stop Failed: %s", errMsg)
		return &pbuf.Status{ErrCode: false, Message: &errMsg}, err
	}
	leftMotor, err := ev3dev.TachoMotorFor("ev3-ports:outA", "lego-ev3-l-motor")
	if err != nil {
		errMsg := "Error getting right motor"
		fmt.Printf("Stop Failed: %s", errMsg)
		return &pbuf.Status{ErrCode: false, Message: &errMsg}, err
	}
	rightMotor.Command(STOP)
	leftMotor.Command(STOP)
	rightMotor.Command(RESET)
	leftMotor.Command(RESET)

	return &pbuf.Status{ErrCode: true}, nil
}

func (s *robotServer) Stats(_ context.Context, _ *pbuf.Status) (*pbuf.Status, error) {
	/* TODO */

	return &pbuf.Status{ErrCode: true}, nil
}

func precisionTurn(request *pbuf.TurnRequest) (*pbuf.Status, error) {
	degrees := float64(request.Degrees)
	leftMotor, err := peripherherals.GetMotor("left")
	if err != nil {
		errMsg := "Turn failed: Error getting left motor\n"
		fmt.Printf("%s", errMsg)
		return &pbuf.Status{ErrCode: false, Message: &errMsg}, err
	}
	rightMotor, err := peripherherals.GetMotor("right")
	if err != nil {
		errMsg := "Turn failed: Error getting right motor\n"
		fmt.Printf("%s", errMsg)
		return &pbuf.Status{ErrCode: false, Message: &errMsg}, err
	}
	peripherherals.ResetGyros()
	leftMotor.Command(RESET)
	rightMotor.Command(RESET)

	leftMotor.SetStopAction(HOLD)
	rightMotor.SetStopAction(HOLD)

	var forwardMotor *ev3dev.TachoMotor
	direction := 1.0
	if degrees < 0 {
		direction = -1
		forwardMotor = rightMotor
	} else {
		direction = 1
		forwardMotor = leftMotor
	}
	cmPerDeg := RobotWidth * 2 * math.Pi / 360.0
	cmPerPulse := WheelDiameter * math.Pi / float64(forwardMotor.CountPerRot())
	motorPos := math.Round(degrees * direction * cmPerDeg / cmPerPulse)
	forwardMotor.SetPositionSetpoint(int(motorPos))
	forwardMotor.SetSpeedSetpoint((forwardMotor.MaxSpeed() * 6) / 10)
	forwardMotor.SetRampUpSetpoint(500 * time.Millisecond)
	forwardMotor.Command(REL_POS)
	time.Sleep(1 * time.Second)
	gyroDeg, gyroCount, gErr := peripherherals.GetGyroValue()
	if gyroCount == 0 {
		rightState, _ := rightMotor.State()
		leftState, _ := leftMotor.State()
		errMsg := "Turn failed: Error reading gyro" +
			"\n\tRight state: " + rightState.String() + "\tLeft state:" + leftState.String() +
			"\n\tAngle: " + strconv.FormatFloat(gyroDeg, 'g', -1, 32) + "\n"
		fmt.Printf("%s", errMsg)
		rightMotor.Command(STOP)
		leftMotor.Command(STOP)
		return &pbuf.Status{ErrCode: false}, gErr
	}
	if math.Abs(float64(degrees)-gyroDeg) < 1.5 {
		return &pbuf.Status{ErrCode: true}, nil
	}
	offset := "Offset is: " + strconv.FormatFloat(degrees-gyroDeg, 'g', -1, 32)
	return &pbuf.Status{ErrCode: false, Message: &offset}, nil
}
