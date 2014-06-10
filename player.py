import pyaudio
import wave
import random
import subprocess
import socket
import json

subprocess.Popen(["python", "../../OpenViBE_accessory/playSound_udp.py"])
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
stimuliName = ["audio/lu.wav", "audio/ru.wav", "audio/rd.wav", "audio/ld.wav"]

class MyOVBox(OVBox):
    def __init__(self):
        OVBox.__init__(self)
        self.stimLabel = None
        self.stimNum = None
        self.trial = None
        self.cursor = 0
        self.subCount = 0
        self.count = 0
        self.untilStart = 0
        self.sequence = []
        self.final = self.doCount

    def initialize(self):
        self.stimLabel = self.setting["Stimulation"]
        self.duration = int(self.setting["oneStimulusDuration"])
        self.interval = float(self.setting["changingInterval"])
        self.stimNum = int(self.setting["stimuliNum"])
        self.stimLabels = ["OVTK_StimulationId_Label_0"+str(i) for i in range(self.stimNum+1)]
        self.trial = int(self.setting["trialsPerStimulus"])
        self.untilStart = int(self.setting["untilStart"])
        self.allTrial = self.Num * self.trial
        seqFileName = self.setting["Random sequence file path"] #path
        self.sequence = self.randomSequence()
        with open(seqFileName, "w") as f:
            f.write(json.dumps(self.sequence)[1:-1])
        self.stimCodes = [OpenViBE_stimulation[self.stimLabels[i]] for i in range(self.stimNum+1)]
        self.output[0].append(OVStimulationHeader(0.,0.))
        return

    def randomSequence(self):
        a = [i for i in range(1, self.stimNum+1)]
        random.shuffle(a)
        seq = a[:]
        i = 1
        while i < self.trial:
            a = seq[-self.stimNum:]
            first = random.choice(a[:-1])
            b = a[:a.index(first)] + a[a.index(first)+1:]
            random.shuffle(b)
            seq += ([first]+b[:])
            i += 1
        return seq

    def uninitialize(self):
        end = self.getCurrentTime()
        self.output[0].append(OVStimulationEnd(end, end))
        udp.sendto("finish", ("127.0.0.1", 12345))#close udp port
        return

    def doCount(self):
        self.count += 1

    def doSubCount(self):
        self.subCount += 1

    def generateStimulation(self, codesIdx):
        stimSet = OVStimulationSet(self.getCurrentTime(), self.getCurrentTime()+1./self.getClock())
        stimSet.append(OVStimulation(self.stimCodes[codesIdx], self.getCurrentTime(), 0.))
        self.output[0].append(stimSet)
        
    def process(self):
        if self.getCurrentTime() >= self.untilStart:
            if self.count and self.count % self.duration == 0:
                stimuNum = self.sequence[self.cursor]
                self.generateStimulation(stimuNum)
                self.cursor += 1
                self.count = 0
                self.final = self.doSubCount
                #temporaly, this uses subprocess.Popen to reduce (maybe visually) latency
                udp.sendto(str(stimuNum-1), ("127.0.0.1", 12345))
            elif self.subCount == self.interval:
                #redundant stimulus to makesure the start of new tartget
                self.generateStimulation(0) 
                self.final = self.doCount
                self.subCount = 0
        elif self.cursor >= self.allTeial:
            self.output[1].append("Some stimuli to stop processing.") #TODO
        self.final()

box = MyOVBox()
