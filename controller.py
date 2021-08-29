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


if __name__ == '__main__':
    hw = Hardware()
