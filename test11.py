from googlesearch import search

query = "中華民國"

for result in search(query, num_results=3, lang='zh-TW', safe='off', advanced=True):
    print(result.title)
    print(result.description)
    print(result.url)
    print()