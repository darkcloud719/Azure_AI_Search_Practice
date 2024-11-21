import os,json
import azure.cognitiveservices.speech as speechsdk
from dotenv import load_dotenv

def text_to_speech():

    speech_key = os.getenv("AZURE_SPEECH_KEY")
    speech_region = os.getenv("AZURE_SPEECH_REGION")
    speech_config = speechsdk.SpeechConfig(subscription=speech_key, region=speech_region)

    speech_config.speech_synthesis_voice_name = "en-US-AriaNeural"
    # speech_config.speech_synthesis_voice_name = "zh-TW-YunJheNeural"
    # speech_config.speech_synthesis_voice_name = "zh-TW-HsiaoChenNeural"
    
    audio_config = speechsdk.audio.AudioOutputConfig(use_default_speaker=True)
    synthesizer = speechsdk.SpeechSynthesizer(speech_config=speech_config, audio_config=audio_config)

    # result = synthesizer.speak_text_async("今天你好嗎?").get()
    result = synthesizer.speak_text_async("Hello, how is your day?").get()

    if result.reason == speechsdk.ResultReason.SynthesizingAudioCompleted:
        print("Speech synthesis completed.")
    elif result.reason == speechsdk.ResultReason.Canceled:
        cancellation_details = result.cancellation_details
        print(f"Speech synthesis canceled: {cancellation_details.reason}")
        if cancellation_details.error_details:
            print(f"Error details: {cancellation_details.error_details}")
    

def main():

    text_to_speech()

if __name__ == "__main__":
    load_dotenv()
    main()