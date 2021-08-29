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


if __name__ == '__main__':
    hw = Hardware()
