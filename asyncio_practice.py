import time
import asyncio

def download_page(url):
    print(f"Starting download from {url}")
    time.sleep(2)
    print(f"Finished download from {url}")

def main_sync():
    start_time = time.time()
    download_page("http://example.com/page1")
    download_page("http://example.com/page2")
    print(f"Total time (sync): {time.time() - start_time} seconds")

async def download_page_async(url):
    print(f"Starting download from {url}")
    await asyncio.sleep(2)
    print(f"Finished download from {url}")

async def main_async():
    start_time = time.time()
    await asyncio.gather(
        download_page_async("http://example.com/page1"),
        download_page_async("http://example.com/page2")
    )
    print(f"Total time (async): {time.time() - start_time} seconds")

if __name__ == "__main__":
    # main_sync()
    asyncio.run(main_async())