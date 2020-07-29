from bluepy.btle import Scanner, DefaultDelegate, Peripheral
from time import sleep


class Blind(DefaultDelegate, Peripheral):
    CHAR_UUID = "0000fe51-0000-1000-8000-00805f9b34fb"
    ROOT_CMD=b'\x00\xff\x00\x00\x9a'
    BASIC_CMD=ROOT_CMD + b'\x0a\x01'
    SETTING_CMD=ROOT_CMD + b'\x22\x03'
    battery_level = None
    blind_position= None


    # Calculate the checksum for the blinds protocol
    def checksum(self, cmd):
        s = 0
        for x in cmd:
            s  = s ^ x
        return bytes([s ^ 0xff])

    def write(self, cmd):
        self.c.write(cmd + self.checksum(cmd))
        sleep(0.1) # To allow for notifications to circulate

    def __init__(self):
        DefaultDelegate.__init__(self)
        Peripheral.__init__(self)
        self.setDelegate(self)


    def connect(self, address):
        Peripheral.connect(self, address)
        if self.__get_char():
            self.__init_seq()
            self.update()
            return True
        else:
            self.disconnect()
            return False

    def __get_char(self):
        serv = self.getServices()
        for s in serv:
            cs = s.getCharacteristics()
            for c in cs:
                if c.uuid == self.CHAR_UUID:
                    self.c = c
                    return True
        return False

    def handleNotification(self, cHandle, data):
        #print("Notification", cHandle, [d for d in data])
        if len(data) == 8:
            if data[0] == 0x9a and data[1] == 0xa1:
                print("---- Blind at " + str(data[4]) + "%")
                self.blind_position = data[4]
        elif len(data) == 9:
            if data[0] == 0x9a and data[1] == 0xa2:
                print("---- Battery at " + str(data[7]) + "%")
                self.battery_level = data[7]
        elif len(data) == 11:
            if data[0] == 0x9a and data[1] == 0xa7:
                print("---- Blind at " + str(data[5]) + "%")
                self.blind_position = data[5]

    def update(self):
        self.query()
        self.battery_query()
        sleep(0.25)

    def query(self):
        self.write(self.ROOT_CMD + b'\xa1\x01\x5a')

    def battery_query(self):
        self.write(self.ROOT_CMD + b'\xa2\x01\x5a') #\x31 - checksum

    def stop(self):
        self.write(self.BASIC_CMD + b'\xcc')

    def open(self):
        self.write(self.BASIC_CMD + b'\xdd')

    def close(self):
        self.write(self.BASIC_CMD + b'\xee')

    def set_upper(self):
        self.write(self.SETTING_CMD + b'\x00\x01\x00')

    def accept_upper(self):
        self.write(self.SETTING_CMD + b'\x20\x01\x00')

    def set_lower(self):
        self.write(self.SETTING_CMD + b'\x00\x02\x00')

    def accept_lower(self):
        self.write(self.SETTING_CMD + b'\x20\x02\x00')

    def open_p(self, percent):
        if percent >= 0 and percent <= 100:
            self.write(self.ROOT_CMD + b'\x0d\x01' + bytes([percent]))
        else:
            print("Invalid percentage")

    def __write_custom(self, cmd):
        bcmd = bytes.fromhex(cmd)
        self.write(bcmd)
        sleep(0.1) # To allow for notifications to circulate

    def __init_seq(self):
        # Mystery sequence snooped from wireshark
        self.__write_custom("00ff00009a170222b815")
        self.__write_custom("00ff00009aa701013d")
        self.__write_custom("00ff00009aa7015a31")
        self.__write_custom("00ff00009a140404111e0e8f")
        self.__write_custom("00ff00009aa2010138")
        self.__write_custom("00ff00009aa2015a31")
        self.__write_custom("00ff00009aa1015a31")
        
