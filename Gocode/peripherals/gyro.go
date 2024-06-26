package peripherals

import (
	"fmt"
	"github.com/ev3go/ev3dev"
	"strconv"
	"time"
)

func ResetGyros() {
	gyro1, err1 := ev3dev.SensorFor("ev3-ports:in1", "lego-ev3-gyro")
	gyro2, err2 := ev3dev.SensorFor("ev3-ports:in4", "lego-ev3-gyro")

	if err1 != nil && err2 != nil {
		errMsg := "Couldn't get gyros for reset"
		fmt.Printf("Gyro Error: %s\n", errMsg)
		return
	} else if err1 != nil {
		gyro2.SetMode("GYRO-CAL")
		time.Sleep(10 * time.Millisecond)
		gyro2.SetMode("GYRO-ANG")
		return
	} else if err2 != nil {
		gyro1.SetMode("GYRO-CAL")
		time.Sleep(10 * time.Millisecond)
		gyro1.SetMode("GYRO-ANG")
		gyro1.SetMode("GYRO-ANG")
		return
	}
	gyro1.SetMode("GYRO-CAL")
	gyro2.SetMode("GYRO-CAL")

	time.Sleep(10 * time.Millisecond)

	gyro1.SetMode("GYRO-ANG")
	gyro2.SetMode("GYRO-ANG")

	gyro1.SetPollRate(5 * time.Millisecond)
	gyro2.SetPollRate(5 * time.Millisecond)

}
func GetGyroValue() (float64, int, error) {
	gyro1, err := ev3dev.SensorFor("ev3-ports:in1", "lego-ev3-gyro")

	gyro2, err2 := ev3dev.SensorFor("ev3-ports:in4", "lego-ev3-gyro")
	if err != nil && err2 != nil {
		errMsg := "Couldn't get gyros for reading values"
		fmt.Printf("Gyro Error: %s\nGyro 1: %s\tGyro 2: %s\n", errMsg, err, err2)
		return 0, 0, err
	} else if err != nil {
		tmp, vErr := gyro2.Value(0)
		if vErr != nil {
			fmt.Printf("Gyro Error: %s\nGyro 1: %s\tGyro 2: %s\n", vErr, err, err2)
			return 0, 0, vErr
		}
		pos2, pErr := strconv.ParseFloat(tmp, 32)
		if pErr != nil {
			fmt.Printf("Gyro Error: %s\nGyro 1: %s\tGyro 2: %s\n", pErr, err, err2)
			return 0, 0, pErr
		}
		return pos2, 1, nil
	} else if err2 != nil {
		tmp, vErr := gyro1.Value(0)
		if vErr != nil {
			fmt.Printf("Gyro Error: %s\nGyro 1: %s\tGyro 2: %s\n", vErr, err, err2)
			return 0, 0, vErr
		}
		pos1, pErr := strconv.ParseFloat(tmp, 32)
		if pErr != nil {
			fmt.Printf("Gyro Error: %s\nGyro 1: %s\tGyro 2: %s\n", pErr, err, err2)
			return 0, 0, pErr
		}
		return pos1, 1, nil
	}
	tmp, vErr := gyro1.Value(0)
	if vErr != nil {
		fmt.Printf("Gyro Error: %s\nGyro 1: %s\tGyro 2: %s\n", vErr, err, err2)
		return 0, 0, vErr
	}
	pos1, pErr := strconv.ParseFloat(tmp, 32)
	if pErr != nil {
		fmt.Printf("Gyro Error: %s\nGyro 1: %s\tGyro 2: %s\n", pErr, err, err2)
		return 0, 0, pErr
	}
	tmp, vErr = gyro2.Value(0)
	if vErr != nil {
		fmt.Printf("Gyro Error: %s\nGyro 1: %s\tGyro 2: %s\n", vErr, err, err2)
		return 0, 0, vErr
	}
	pos2, pErr := strconv.ParseFloat(tmp, 32)
	if pErr != nil {
		fmt.Printf("Gyro Error: %s\nGyro 1: %s\tGyro 2: %s\n", pErr, err, err2)
		return 0, 0, pErr
	}
	return (pos1 + pos2) / 2.0, 2, nil
}
