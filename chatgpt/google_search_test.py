import os
import openai
import json
import tiktoken
from dotenv import load_dotenv
from rich import print as pprint
from googlesearch import search

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")
openai.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
openai.api_version = os.getenv("OPENAI_API_VERSION")
openai.api_type = "azure"

hist = []
backtrace = 2

# q:"如果我想知道以下這件事，請確認是否需要網路搜尋才做得到?" translate it into Eng.
# a: "If I want to know the following, do I need to search the internet to do it?"
# q:"如果需要,請以下列json格式回答我，除了json格式之料外，不要加上額外資訊，就算你知道答案，也不要回覆:" translate it into Eng.
# a: "If necessary, please answer me in the following json format. Do not add additional information other than the json format. Even if you know the answer, do not reply."
# q:"你建議的搜尋關鍵字" translate This sentence into Eng.
# a: "The keyword you suggest to search"
# q:"如果不需要，請以下列json格式回答我:" translate it into Eng.
# a: "If not necessary, please answer me in the following json format:"

template_google = '''
If I want to know the following, do I need to search the internet to do it?

```
{}
```

If necessary, please answer me in the following json format. Do not add additional information other than the json format. Even if you know the answer, do not reply.

```
{{
    "search":"Y",
    "keyword":"The keyword you suggest to search"
}}

```
If not necessary, please answer me in the following json format:

```
{{
    "search":"N",
    "keyword":""
}}
```
'''

# q: "請用JSON回復" translate it into Eng.
# a: "Please reply with JSON"

def get_reply_g(messages, stream=False, json_format=False):
    try:
        json_msg = [
            {"role":"system","content":"Please reply with JSON"} if json_format else []
        ]

        response = openai.chat.completions.create(
            model = os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages = messages + json_msg if json_msg else messages,
            # stream = stream,
            response_format = {
                "type":"json_object" if json_format else "text"
            }
        )

        return response.choices[0].message.content

    except openai.APIError as err:
        reply = f"Error: {err.message}"
        return reply

def check_google(hist, msg, stream, verbose=False):
    reply = get_reply_g(hist + [{"role":"user","content":template_google.format(msg)}], stream=stream, json_format=True)
    # full_reply = ""
    # if stream:
    #     for ans in reply:
    #         full_reply += ans
    #     if verbose: print(full_reply)
    # else:
    #     full_reply = reply
    #     if verbose: print(full_reply)
    return reply


def chat_g(sys_msg, user_msg, stream=False, verbose=False):

    global hist
    
    ans = json.loads(check_google(hist, user_msg, stream=stream, verbose=verbose))
    if verbose:
        print(f"ans:{ans}")
    print(ans)

    


def main():

    sys_msg = input("What do you want AI to be:")

    if not sys_msg.strip():
        sys_msg = "You are a helpful assistant."

    print()

    while True:
        msg = input("You:")
        if not msg.strip():
            break
        reply = chat_g(sys_msg, msg, stream=True, verbose=True)
        print(reply)
        # for reply in chat_g(sys_msg, msg, stream=True, verbose=True):
        #     print(reply, end="")
        # print("\n")

if __name__ == "__main__":
    main()