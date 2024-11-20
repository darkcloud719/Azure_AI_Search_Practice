import os
import openai
from dotenv import load_dotenv
from rich import print as pprint
from rich.console import Console
from rich.table import Table

all_hist = []
hist = []
backtrace = 2

console = Console()

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = os.getenv("OPENAI_API_VERSION")
openai.api_type = "azure"

def chat(sys_msg, user_msg):
    global hist, all_hist

    if len(hist) == 0:
        hist.append({"role":"system","content":sys_msg})
        all_hist.append({"role":"system","content":sys_msg})
    
    hist.append({"role":"user","content":user_msg})
    all_hist.append({"role":"user","content":user_msg})

    reply_full = ""
    for reply in get_reply(hist + [{"role":"user","content":user_msg}]):
        reply_full += reply
        yield reply
    hist.append({"role":"assistant","content":reply_full})
    all_hist.append({"role":"assistant","content":reply_full})
    hist = hist[-2*backtrace:]


def get_reply(messages):

    try:
        response = openai.chat.completions.create(
            model = os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages = messages,
            stream = True
        )

        for chunk in response:
            if chunk.choices and chunk.choices[0].delta:
                yield chunk.choices[0].delta.content or ''
    except openai.APIError as err:
        reply = f"Error: {err.message}"
        print(reply)
        console.print(reply, sytle="bold red")

def print_hist(history):

    table = Table(title="Chat History", style="cyan")
    table.add_column("Role", justify="left", style="magenta")
    table.add_column("Content", justify="left", style="green")

    for item in history:
        table.add_row(item["role"], item["content"])

    console.print(table)

def main():

    sys_msg = input("What system prompt do you want to use: ") 

    if not sys_msg.strip():
        sys_msg = "You are a helpful assistant!"

    print()

    while True:
        msg = input("You:")
        if not msg.strip():
            break
        for reply in chat(sys_msg, msg):
            print(reply, end="")
        print("\n")

    # print(f"All prompts: {hist}")
    print_hist(all_hist)

if __name__ == "__main__":
    load_dotenv()
    main()

       