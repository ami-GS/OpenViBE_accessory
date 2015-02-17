import socket

class UDPSend(OVBox):
    def __init__(self):
        OVBox.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.host = None
        self.port = None

    def initialize(self):
        self.host = self.setting["Host name"]
        self.port = int(self.setting["Port"])

    def process(self):
        self.socket.sendto("hello", (self.host, self.port))

    def uninitialize(self):
        return

box = UDPSend()
