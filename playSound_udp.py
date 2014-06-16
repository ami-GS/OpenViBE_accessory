import socket
import pyaudio
import wave

p = pyaudio.PyAudio()
wf = []
stream = []
CHUNK = 4096
stimuliName = ["audio/lu.wav", "audio/ld.wav", "audio/rd.wav", "audio/ru.wav"]
content = []

for i in range(len(stimuliName)):
    wf.append(wave.open(stimuliName[i], "rb"))
    stream.append(p.open(format=p.get_format_from_width(wf[i].getsampwidth()),
                         channels = wf[i].getnchannels(),
                         rate = wf[i].getframerate(),
                         output=True))

def readContent():
    for i in range(len(stimuliName)):
        data = wf[i].readframes(CHUNK)
        tmp = []
        while data:
            tmp.append(data)
            data = wf[i].readframes(CHUNK)
        content.append(tmp)

def playOnMemory(fNum):
    for data in content[fNum]:
        stream[fNum].write(data)


def playFromFile(fNum):
    data = wf[fNum].readframes(CHUNK)
    while data:
        stream[fNum].write(data)
        data = wf[fNum].readframes(CHUNK)
    else:
        wf[fNum] = wave.open(stimuliName[fNum], "rb")

if __name__ == "__main__":
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    udp.bind(("127.0.0.1", 12345))
    play = playOnMemory # read file only once
    #play = playFromFile # read file in each call
    readContent()
    while True:
        fNum, addr = udp.recvfrom(128)
        if fNum == "finish":
            break
        else:
            play(int(fNum))
    
    for i in range(len(stimuliName)):
        wf[i].close()
        stream[i].close()
    udp.close()
        
