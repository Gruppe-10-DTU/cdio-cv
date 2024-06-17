package peripherals

import (
	"errors"
	"github.com/ev3go/ev3dev"
	"strings"
)

func GetMotor(inp string) (*ev3dev.TachoMotor, error) {
	side := strings.ToLower(inp)
	switch side {
	case "left":
		return ev3dev.TachoMotorFor("ev3-ports:outA", "lego-ev3-l-motor")
	case "right":
		return ev3dev.TachoMotorFor("ev3-ports:outD", "lego-ev3-l-motor")
	}
	return nil, errors.New("please input side")
}

func BothMotorsRunning() bool {
	leftMotor, err := GetMotor("left")
	if err != nil {
		return false
	}

	rightMotor, err := GetMotor("right")
	if err != nil {
		return false
	}
	leftState, _ := leftMotor.State()
	rightState, _ := rightMotor.State()
	leftString := leftState.String()
	rightString := rightState.String()
	leftMotorRunning := strings.Contains(leftString, "running") || strings.Contains(leftString, "ramping")
	rightMotorRunning := strings.Contains(rightString, "running") || strings.Contains(rightString, "ramping")
	return leftMotorRunning && rightMotorRunning
}
