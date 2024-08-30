from tenacity import retry, wait_random_exponential, stop_after_attempt

@retry(wait=wait_random_exponential(min=1, max=5), stop=stop_after_attempt(5))
def _test():

    try:
        print("Test started")
    
        10 / 0
    except Exception as ex:
        print(f"Exception happened: {ex}")

if __name__ == "__main__":
    _test()