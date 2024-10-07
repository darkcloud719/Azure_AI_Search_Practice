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

template_google = '''

```
{}
```

If necessary, please responsd in the following json format. Do not add additional information other than the json format. Even if you know the answer, do not reply.

```
{{
    "search":"Y",
    "keyword":"The keyword you suggest to search"
}}
```

If not necessary, please respond in the following json format:

```
{{
    "search":"N",
    "keyword":""
}}
```
'''

def get_reply_g(messages, stream=True, json_format=False):
    try:
        json_msg = [
            {"role":"system","content":"Please reply with JSON"}
        ] if json_format else []
        response = openai.chat.completions.create(
            model = os.getenv("AZURE_OPENAI_DEPLOYMENT"),
            messages = messages + json_msg,
            stream = stream,
            response_format = {"type":"json_object"} if json_format else "text"
        )

        if stream:
            for res in response:
                if res.choices:
                    print(res.choices[0].delta.content)
                    yield res.choices[0].delta.content or ''
        else:
            yield response.choices[0].message.content


            # for chunk in response:
            # if chunk.choices:
            #     yield chunk.choices[0].delta.content or ''

    except openai.APIError as err:
        reply = f"Error: {err.message}"
        print(reply)
        yield reply

def check_google(hist, msg, verbose=False):
    reply = get_reply_g(
        hist + [{"role":"user","content":template_google.format(msg)}], json_format=True
    )

    # for ans in reply:pass
    full_reply = ""
    for ans in reply:
        full_reply += ans
    if verbose: 
        print(full_reply)
    return ans


def main():
    ans = check_google([], "What is the highest mountain in the Taiwan?", True)

if __name__ == "__main__":
    main()

