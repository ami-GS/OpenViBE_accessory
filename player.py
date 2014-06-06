import pyaudio
import wave
import random
from threading import Thread
import time

CHUNK = 4096
p = pyaudio.PyAudio()
wf = []
stream = []
stimuliName = ["tm2_switch000.wav", "tm2_switch001.wav", "tm2_swing002.wav", "tm2_swing004.wav"]

class MyOVBox(OVBox):
    def __init__(self):
        OVBox.__init__(self)
        self.stimLabel = None
        self.stimCode = None
        self.stimNum = None
        self.trial = None
        self.cursor = 0
        self.subCount = 0
        self.count = 0
        self.sequence = []
        self.final = self.doCount
        for i in range(len(stimuliName)):
            wf.append(wave.open(stimuliName[i], "rb"))
            stream.append(p.open(format=p.get_format_from_width(wf[i].getsampwidth()),
                                 channels = wf[i].getnchannels(),
                                 rate = wf[i].getframerate(),
                                 output=True))

    def initialize(self):
        self.stimLabel = self.setting["Stimulation"]
        self.duration = int(self.setting["oneStimulusDuration"])
        self.interval = float(self.setting["changingInterval"])
        self.stimNum = int(self.setting["stimuliNum"])
        self.stimSet = ["OVTK_StimulationId_Label_0"+str(i) for i in range(self.stimNum+1)]
        print self.stimSet
        self.trial = int(self.setting["trialsPerStimulus"])
        self.sequence = self.randomSequence()
        print self.sequence
        self.stimCode = OpenViBE_stimulation[self.stimLabel]
        self.output[0].append(OVStimulationHeader(0.,0.))
        return

    def randomSequence(self):
        a = [i for i in range(len(stimuliName))]
        random.shuffle(a)
        seq = a[:]
        i = 1
        while i < self.trial:
            a = seq[-len(stimuliName):]
            first = random.choice(a[:-1])
            b = a[:a.index(first)] + a[a.index(first)+1:]
            random.shuffle(b)
            seq += ([first]+b[:])
            i += 1
        return seq

    def uninitialize(self):
        return

    def generateStimulation(self):
        stimSet = OVStimulationSet(self.getCurrentTime(), self.getCurrentTime()+1./self.getClock())
        stimSet.append(OVStimulation(self.stimCode, self.getCurrentTime(), 0.))
        self.output[0].append(stimSet)

    def doCount(self):
        self.count += 1

    def doSubCount(self):
        self.subCount += 1

    def threadControl(self):
        for i in range(5):
            print(i)

    def makeSound(self, stimuNum):
        data = wf[stimuNum].readframes(CHUNK)
        self.cursor += 1
        while data:
            stream[stimuNum].write(data)
            data = wf[stimuNum].readframes(CHUNK)
        else:
            #open again
            wf[stimuNum] = wave.open(stimuliName[stimuNum], "rb")
        
        

    def process(self):
        #TODO playing sound frequencies should be obtained from settings
        if self.count and self.count % self.duration == 0:
            self.generateStimulation()
            stimuNum = self.sequence[self.cursor]
            self.count = 0
            self.final = self.doSubCount
            self.t = Thread(target=self.makeSound, args=(stimuNum,))
            self.t.start()
            self.t.join() 
            #I noticed this is nonsens to use thread, because this above line stops everything.

        elif self.subCount == self.interval:
            self.generateStimulation()
            self.final = self.doCount
            self.subCount = 0

        self.final()

box = MyOVBox()
