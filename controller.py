import pyvisa
import numpy as np
import time
import datetime


class Hardware(object):
    def __init__(self):
        self.R8240_GPIB_id = 1
        self.E3647A_GPIB_id = 2


if __name__ == '__main__':
    hw = Hardware()
