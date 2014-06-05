import pyaudio
import wave

CHUNK = 1024
p = pyaudio.PyAudio()
wf = []
stream = []
stimuliName = ["tm2_switch000.wav", "tm2_switch001.wav"]

class MyOVBox(OVBox):
    def __init__(self):
        OVBox.__init__(self)
        self.stimLabel = None
        self.stimCode = None
        for i in range(len(stimuliName)):
            wf.append(wave.open(stimuliName[i], "rb"))
            stream.append(p.open(format=p.get_format_from_width(wf[i].getsampwidth()),
                                 channels = wf[i].getnchannels(),
                                 rate = wf[i].getframerate(),
                                 output=True))

        #TODO make random sequence
        self.sequence = [0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
        self.cursor = 0
        self.second = 0

    def initialize(self):
        return

    def uninitialize(self):
        return

    def process(self):
        #TODO playing sound frequencies should be obtained from settings
        if self.second % 5 == 0:
            #TODO stimulus output should be here
            stimuNum = self.sequence[self.cursor]
            data = wf[stimuNum].readframes(CHUNK)
            while data:
                stream[stimuNum].write(data)
                data = wf[stimuNum].readframes(CHUNK)
            else:
                wf[stimuNum] = wave.open(stimuliName[stimuNum], "rb")
            self.cursor += 1
        elif self.second % 6 == 0:
            #do something
            pass
        print self.second
        self.second += 1

box = MyOVBox()
        
