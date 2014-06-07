import socket
import pyaudio
import wave

p = pyaudio.PyAudio()
wf = []
stream = []
CHUNK = 4096
#stimuliName = ["tm2_switch000.wav", "tm2_switch001.wav",
#               "tm2_swing002.wav", "tm2_swing004.wav"]
stimuliName = ["audio/lu.wav", "audio/ru.wav", "audio/rd.wav", "audio/ld.wav"]


for i in range(4):
    wf.append(wave.open(stimuliName[i], "rb"))
    stream.append(p.open(format=p.get_format_from_width(wf[i].getsampwidth()),
                         channels = wf[i].getnchannels(),
                         rate = wf[i].getframerate(),
                         output=True))

def play(fNum):
    data = wf[fNum].readframes(CHUNK)
    while data:
        stream[fNum].write(data)
        data = wf[fNum].readframes(CHUNK)
    else:
        wf[fNum] = wave.open(stimuliName[fNum], "rb")
        
    

if __name__ == "__main__":
    udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

    udp.bind(("127.0.0.1", 12345))
    while True:
        fNum, addr = udp.recvfrom(128)
        if fNum == "finish":
            break
        else:
            play(int(fNum))

    udp.close()
        
