package peripherals

import "github.com/ev3go/ev3dev"

func BothMotorsRunning() bool {
	leftMotor, err := ev3dev.TachoMotorFor("ev3-ports:outA", "lego-ev3-l-motor")
	if err != nil {
		return false
	}

	rightMotor, err := ev3dev.TachoMotorFor("ev3-ports:outD", "lego-ev3-l-motor")
	if err != nil {
		return false
	}
	leftRunning, _ := leftMotor.State()
	rightRunning, _ := rightMotor.State()
	//fmt.Printf("left: %s\tright: %s\n", leftRunning, rightRunning)
	return (leftRunning == ev3dev.Running || leftRunning == ev3dev.Ramping) && (rightRunning == ev3dev.Running || rightRunning == ev3dev.Ramping)
}
