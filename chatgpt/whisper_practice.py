import os,json,openai
from dotenv import load_dotenv
from rich import print as pprint
import pyaudio
import wave


openai.api_key = os.getenv("OPENAI_API_KEY")
openai.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = os.getenv("OPENAI_API_VERSION")
openai.api_type = "azure"

def record_audio(duration=5, rate=48000, channels=4, chunk=1024):

    p = pyaudio.PyAudio()

    stream = p.open(format=pyaudio.paInt16,
                    channels=channels,
                    rate=rate,
                    input=True,
                    frames_per_buffer=chunk)
    
    print("Recording...")
    frames = []
    for i in range(0,int(rate / chunk * duration)):
        data = stream.read(chunk)
        frames.append(data)

    print("Finish recording.")
    stream.stop_stream()
    stream.close()
    p.terminate()

    audio_data = b''.join(frames)
    return audio_data

def save_as_wav(audio_data, filename="recorded_audio.wav", rate=48000, channels=4):

    with wave.open(filename,'wb') as wf:
        wf.setnchannels(channels)
        wf.setsampwidth(2)
        wf.setframerate(rate)
        wf.writeframes(audio_data)

    print(f"Audio saved as '{filename}'")

def list_audio_devices():

    p = pyaudio.PyAudio()
    device_count = p.get_device_count()
    for i in range(device_count):
        print(p.get_device_info_by_index(i))
    
def recognize_audio_by_whisper(filename="recorded_audio.wav"):

    result = openai.audio.transcriptions.create(
        file=open(filename,"rb"),
        model="whisper"
    )

    pprint(result)

def main():

    audio_data = record_audio(duration=5)

    print(f"Audio data length: {len(audio_data)} bytes")

    save_as_wav(audio_data)

    recognize_audio_by_whisper("recorded_audio.wav")

    # list_audio_devices()
if __name__ == "__main__":
    load_dotenv()
    main()

