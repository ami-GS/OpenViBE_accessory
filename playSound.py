import wave
import pyaudio
import sys


CHUNK = 4096
def play(fname):
    p = pyaudio.PyAudio()
    wf = wave.open(fname, "rb")
    stream = (p.open(format=p.get_format_from_width(wf.getsampwidth()),
                         channels = wf.getnchannels(),
                         rate = wf.getframerate(),
                         output=True))
    
    data = wf.readframes(CHUNK)
    while data:
        stream.write(data)
        data = wf.readframes(CHUNK)
    
    wf.close()
    stream.close()

if __name__ == "__main__":
    play(sys.argv[1])
