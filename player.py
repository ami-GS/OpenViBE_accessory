import pyaudio
import wave
import random
#from threading import Thread
#from multiprocessing import Process
import subprocess
import time
import socket

subprocess.Popen(["python", "../../OpenViBE_accessory/playSound_udp.py"])
udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
#CHUNK = 4096
#p = pyaudio.PyAudio()
#wf = []
#stream = []
#stimuliName = ["tm2_switch000.wav", "tm2_switch001.wav",
#               "tm2_swing002.wav", "tm2_swing004.wav"]
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
        """
        for i in range(len(stimuliName)):
            wf.append(wave.open(stimuliName[i], "rb"))
            stream.append(p.open(format=p.get_format_from_width(wf[i].getsampwidth()),
                                 channels = wf[i].getnchannels(),
                                 rate = wf[i].getframerate(),
                                 output=True))
        """
    def initialize(self):
        self.stimLabel = self.setting["Stimulation"]
        self.duration = int(self.setting["oneStimulusDuration"])
        self.interval = float(self.setting["changingInterval"])
        self.stimNum = int(self.setting["stimuliNum"])
        self.stimLabels = ["OVTK_StimulationId_Label_0"+str(i) for i in range(self.stimNum+1)]
        self.trial = int(self.setting["trialsPerStimulus"])
        self.untilStart = int(self.setting["untilStart"])
        self.sequence = self.randomSequence()
        print self.sequence
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
    """
    def makeSound(self, stimuNum):
        data = wf[stimuNum].readframes(CHUNK)
        while data:
            stream[stimuNum].write(data)
            data = wf[stimuNum].readframes(CHUNK)
        else:
            #open again
            wf[stimuNum] = wave.open(stimuliName[stimuNum], "rb")
    """
    def generateStimulation(self, codesIdx):
        stimSet = OVStimulationSet(self.getCurrentTime(), self.getCurrentTime()+1./self.getClock())
        print self.stimCodes[codesIdx]
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

                #print subprocess.Popen(["python", "../../OpenViBE_accessory/playSound.py", stimuliName[stimuNum-1]])

                #self.p = Process(target=self.makeSound, args=(stimuNum-1,))
                #self.p.start()
                #self.p.join()
                
                #self.t = Thread(target=self.makeSound, args=(stimuNum-1,))
                #self.t.start()
                #self.t.join() 
                #I noticed this is nonsens to use thread, because this above line stops everything.

            elif self.subCount == self.interval:
                #redundant stimulus to makesure the start of new tartget
                self.generateStimulation(0) 
                self.final = self.doCount
                self.subCount = 0
                
        self.final()

box = MyOVBox()
