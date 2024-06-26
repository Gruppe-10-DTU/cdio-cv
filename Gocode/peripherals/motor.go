package peripherals

import (
	"errors"
	"fmt"
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
		fmt.Printf("Motor Error: %s", err)
		return false
	}

	rightMotor, err := GetMotor("right")
	if err != nil {
		fmt.Printf("Motor Error: %s\n", err)
		return false
	}
	leftState, _ := leftMotor.State()
	rightState, _ := rightMotor.State()
	leftString := leftState.String()
	rightString := rightState.String()
	leftMotorStopped := strings.Contains(leftString, "stalled") || strings.Contains(leftString, "stopped")
	rightMotorStopped := strings.Contains(rightString, "stalled") || strings.Contains(rightString, "stopped")
	return !leftMotorStopped && !rightMotorStopped
}
