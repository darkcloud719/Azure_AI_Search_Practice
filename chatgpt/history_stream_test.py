import os
import openai
from dotenv import load_dotenv
from rich import print as pprint

hist = []
backtrace = 2

def chat(sys_msg, user_msg):
    global hist
    hist.append({"role":"system","content":sys_msg})
    reply_full = ""
    for reply in get_reply(hist + [{"role":"user","content":user_msg}]):
        reply_full += reply
        yield reply
    hist.append({"role":"system","content":reply_full})
    hist = hist[-2*backtrace:]

def get_reply(messages):
    
    openai.api_key = os.getenv("OPENAI_API_KEY")
    openai.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    openai.api_version = os.getenv("OPENAI_API_VERSION")
    openai.api_type = "azure"

    try:
        response = openai.chat.completions.create(
            model = os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages = messages,
            stream = True
        )

        for chunk in response:
            if chunk.choices:
                yield chunk.choices[0].delta.content or ''
    except openai.APIError as err:
        reply = f"Error: {err.message}"
        print(reply)

def main():

    sys_msg = input("What do you want ai to be:")

    if not sys_msg.strip():
        sys_msg = "You are a helpful assistant."
    print()
    while True:
        msg = input("You:")
        if not msg.strip():
            break
        for reply in chat(sys_msg, msg):
            print(reply, end="")
        print("\n")

if __name__ == "__main__":
    load_dotenv()
    main()
