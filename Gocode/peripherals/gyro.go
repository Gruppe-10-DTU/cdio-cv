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
		return
	} else if err1 != nil {
		gyro2.SetMode("GYRO-ANG")
		direct, err := gyro2.Direct(666)
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
		return
	} else if err2 != nil {
		gyro1.SetMode("GYRO-ANG")
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
func GetGyroValue() (float64, int, error) {
	gyro1, err := ev3dev.SensorFor("ev3-ports:in1", "lego-ev3-gyro")

	gyro2, err2 := ev3dev.SensorFor("ev3-ports:in4", "lego-ev3-gyro")
	if err != nil && err2 != nil {
		return 0, 0, err
	} else if err != nil {
		tmp, vErr := gyro2.Value(0)
		if vErr != nil {
			return 0, 0, vErr
		}
		pos2, pErr := strconv.ParseFloat(tmp, 32)
		if pErr != nil {
			return 0, 0, pErr
		}
		return pos2, 1, nil
	} else if err2 != nil {
		tmp, vErr := gyro1.Value(0)
		if vErr != nil {
			return 0, 0, vErr
		}
		pos1, pErr := strconv.ParseFloat(tmp, 32)
		if pErr != nil {
			return 0, 0, pErr
		}
		return pos1, 1, nil
	}
	tmp, vErr := gyro1.Value(0)
	if vErr != nil {
		return 0, 0, vErr
	}
	pos1, pErr := strconv.ParseFloat(tmp, 32)
	if pErr != nil {
		return 0, 0, pErr
	}
	tmp, vErr = gyro2.Value(0)
	if vErr != nil {
		return 0, 0, vErr
	}
	pos2, pErr := strconv.ParseFloat(tmp, 32)
	if pErr != nil {
		return 0, 0, pErr
	}
	fmt.Printf("Current gyro values: %f / %f", pos1, pos2)
	return (pos1 + pos2) / 2.0, 2, nil
}
