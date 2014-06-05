import socket

class MyOVBox(OVBox):
    def __init__(self):
        OVBox.__init__(self)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    def initialize(self):
        return

    def uninitialize(self):
        return

    def process(self):
        host = self.setting["Hostname"]
        port = int(self.setting["port"])
        self.socket.sendto("hello", (host, port))

box = MyOVBox()
        
