import os
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

def continuous_recognition_from_microphone():

    speech_key = os.getenv("AZURE_SPEECH_KEY")
    speech_region = os.getenv("AZURE_SPEECH_REGION")
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)

    speech_config.speech_recognition_language="zh-TW"

    audio_config = speechsdk.audio.AudioConfig(use_default_microphone=True)

    speech_recognizer = speechsdk.SpeechRecognizer(speech_config=speech_config, audio_config=audio_config)

    def recognized_callback(event):
        print(f"Recognized: {event.result.text}")

    # def intermediate_callback(event):
    #     print(f"Intermediate Result: {event.result.text}")

    def canceled_callback(event):
        print(f"Recognition canceled: {event.cancellation_details.reason}")
        if event.cancellation_details.error_details:
            print(f"Error details: {event.cancellation_details.error_details}")

    speech_recognizer.recognized.connect(recognized_callback)
    # speech_recognizer.recognizing.connect(intermediate_callback)
    speech_recognizer.canceled.connect(canceled_callback)

    print("Speak into your microphone. Precc Ctrl+C to stop.")

    speech_recognizer.start_continuous_recognition()

    try:
        while True:
            pass
    except KeyboardInterrupt:
        print("\nStopping continuous recognition...")
        speech_recognizer.stop_continuous_recognition()

def main():
    load_dotenv()
    continuous_recognition_from_microphone()

if __name__ == "__main__":
    main()