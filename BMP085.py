import smbus
import time


class Bmp085(object):

    def __init__(self, address, bus):
        self.address = address
        self.bus_number = bus
        self.bus = smbus.SMBus(bus)
        self.AC1 = self.__read16S(0XAA)
        self.AC2 = self.__read16S(0xAC)
        self.AC3 = self.__read16S(0xAE)
        self.AC4 = self.__read16U(0xB0)
        self.AC5 = self.__read16U(0xB2)
        self.AC6 = self.__read16U(0xB4)
        self.B1 = self.__read16S(0xB6)
        self.B2 = self.__read16S(0xB8)
        self.MB = self.__read16S(0xBA)
        self.MC = self.__read16S(0xBC)
        self.MD = self.__read16S(0xBE)
        #print self.AC1, self.AC2, self.AC3, self.AC4, self.AC5, self.AC6, self.B1, self.B2, self.MB, self.MC, self.MD

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

    def readTempPressure(self):
        # Reading raw temperature.
        self.bus.write_byte_data(self.address, 0xF4, 0x2E)
        time.sleep(0.005)
        UT = self.__read16U(0xF6)
        X1 = ((UT - self.AC6) * self.AC5) >> 15
        X2 = (self.MC << 11) / (X1 + self.MD)
        B5 = X1 + X2
        temp = (int(B5 + 8) >> 4) / 10.0
        # Ultra precise mesur mode for pressure.
        mode = 3
        # Reading raw pressure.
        self.bus.write_byte_data(self.address, 0xF4, 0X34 + (mode << 6))
        time.sleep(0.026)
        msb = self.bus.read_byte_data(self.address,
                                      0xF6)
        lsb = self.bus.read_byte_data(self.address,
                                      0xF7)
        xlsb = self.bus.read_byte_data(self.address,
                                       0xF8)
        UP = ((msb << 16) + (lsb << 8) + xlsb) >> (8 - mode)
        #print "UP", UP
        B6 = B5 - 4000
        X1 = int(self.B2 * int( B6 * B6 ) >> 12 ) >> 11
        X2 = int(self.AC2 * B6) >> 11
        X3 = X1 + X2
        B3 = (((self.AC1 * 4 + X3) << mode) + 2) / 4
        X1 = int(self.AC3 * B6) >> 13
        X2 = int(self.B1 * (int(B6 * B6) >> 12)) >> 16
        X3 = ((X1 + X2) + 2) >> 2
        B4 = (self.AC4 * (X3 + 32768)) >> 15
        B7 = (UP - B3) * (50000 >> mode)
        if (B7 < 0x80000000):
            p = (B7 * 2) / B4
        else:
            p = (B7 / B4) * 2
        X1 = (int(p) >> 8) * (int(p) >> 8)
        X1 = (X1 * 3038) >> 16
        X2 = int(-7357 * p) >> 16
        p = p + ((X1 + X2 + 3791) >> 4)
        return (temp, p)
