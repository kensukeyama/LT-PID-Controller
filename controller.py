import pyvisa
import numpy as np
import time
import datetime


class Hardware(object):
    def __init__(self):
        self.R8240_GPIB_id = 1
        self.E3647A_GPIB_id = 2
        self.GPIBConnection()

    def GPIBConnection(self):

        self.rm = pyvisa.ResourceManager()
        self.device_list = self.rm.list_resources()
        if len(self.device_list) == 0:
            print("Error: GPIB-USB controller is not connected.")
            exit()
        for i in self.device_list:
            if "GPIB"+str(self.R8240_GPIB_id) in i:
                self.R8240 = self.rm.open_resource(i)
            elif "GPIB"+str(self.R8240_GPIB_id) not in i:
                print("Couldn't establish connection with R8240")
                if len(self.device_list) == 2:
                    print("Check GPIB ID!")
                exit()
            elif "GPIB"+str(self.E3647A_GPIB_id) in i:
                self.E3647A = self.rm.open_resource(i)
            elif "GPIB"+str(self.E3647A_GPIB_id) not in i:
                print("Couldn't establish connection with E3647A")
                if len(self.device_list) == 2:
                    print("Check GPIB ID!")
                exit()
        self.deviceInitialize()

    def resetDevices(self):
        self.R8240.write("*RST")
        self.E3647A.write("*RST")

    def deviceInitialize(self):
        self.resetDevices()
        self.R8240.write("F1, R0, IT3, LF1")
        self.E3647A.write("INST:SEL OUT1")
        self.E3647A.write("APPL MIN MAX")

    def getTemperature(self):
        return round(float(self.R8240.query('E').split()[1])*100, 3)

    def setVoltage(self, value):
        # E3647A can control voltage within 2 digit.
        self.E3647A.write(f"VOLT {round(value,2)}")

    def getCurrent(self):
        return round(float(self.E3647A.query("MEAS:CURR?")), 3)


class PID(object):
    def __init__(self):
        self.Kp = 50
        self.Ki = 4
        self.Kd = 1

        self.setpoint = 0
        self.ramp_slope = 3  # Unit: K/min
        # Heater can be applied the voltage at less than 13 V.
        self.max_voltage = 13
        self.Initialize()

    def getCp(self):
        return self.Cp

    def getCi(self):
        return self.Ci

    def getCd(self):
        return self.Cd

    def editSetpoint(self, setpoint):
        self.setpoint = setpoint

    def editRampSlope(self, rampslope):
        self.ramp_slope = rampslope

    def Initialize(self):
        self.current_time = time.time()
        self.current_setpoint = 0
        self.ramp_position = 0
        self.prev_time = self.current_time
        self.prev_temperature = 0
        self.prev_error = 0
        if self.Kd > 0:
            self.Ti = self.Kp/self.Kd
        else:
            self.Ti = 0
        self.Td = self.Kp * self.Kd
        self.Cp = 0
        self.Ci = 0
        self.Cd = 0

    def setupRampSlope(self, current_temperature):
        ramp_slope_sec = self.ramp_slope/60
        number_steps = (self.setpoint-current_temperature) // ramp_slope_sec
        self.ramp_temperature_list = np.array([current_temperature])
        for i in range(1, number_steps + 2):
            if not i == number_steps + 1:
                self.ramp_temperature_list.append(i * ramp_slope_sec + current_temperature)
            else:
                self.ramp_temperature_list.append(self.setpoint)

    def PIDLoop(self, current_temperature):
        if self.ramp_position != len(self.ramp_temperature_list):
            self.current_setpoint = self.ramp_temperature_list[self.ramp_position]
            self.ramp_position += 1

        self.current_time = time.time()
        diff_time = self.current_time-self.prev_time

        error = self.current_setpoint-current_temperature
        self.Cp = error
        self.Ci += error*diff_time
        if self.Ci < 0:
            self.Ci = 0
        self.Cd = (error-self.prev_error)/diff_time
        output = self.Cp * (error + self.Ci/self.Ti + self.Td * self.Cd)    # output (unit: %)

        # Avoid "Integral windup"
        if output >= 100:
            output = 100
            self.Ci -= error*diff_time
        elif output <= 0:
            output = 0

        # Set the previous values from current values
        self.prev_time = self.current_time
        self.prev_error = error

        return output


class Control(object):
    def __init__(self):
        self.test = 0


if __name__ == '__main__':
    hw = Hardware()
