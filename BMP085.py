import smbus
import time


class Bmp085(object):

    def __init__(self, address, bus):
        self.address = address
        self.bus_number = bus
        self.bus = smbus.SMBus(bus)
        self.AC5 = self.__read16U(0xB2)
        self.AC6 = self.__read16U(0xB4)
        self.MC = self.__read16S(0xBC)
        self.MD = self.__read16S(0xBE)

    def __read16S(self, reg):
        hi = self.bus.read_byte_data(self.address,
                                     reg)
        lo = self.bus.read_byte_data(self.address,
                                     reg+1)
        if hi > 256/2:
            hi = hi - 256
        return (hi<<8)+lo

    def __read16U(self, reg):
        hi = self.bus.read_byte_data(self.address,
                                     reg)
        lo = self.bus.read_byte_data(self.address,
                                     reg+1)
        return (hi<<8)+lo

    def readTemp(self):
        self.bus.write_byte_data(self.address, 0xF4, 0x2E)
        time.sleep(0.005)
        UT = self.__read16U(0xF6)
        X1 = ((UT - self.AC6) * self.AC5) >> 15
        X2 = (self.MC << 11) / (X1 + self.MD)
        B5 = X1 + X2
        temp = ((B5 +8) >> 4) / 10.0
        return temp
