import threading 

thread_local_data = threading.local()

def process_data():
    thread_local_data.my_data = threading.current_thread().name
    print(f"Thread {threading.current_thread().name} had data: {thread_local_data.my_data}")

t1 = threading.Thread(target=process_data, name="Thread-1")
t2 = threading.Thread(target=process_data, name="Thread-2")

t1.start()
t2.start()

t1.join()
t2.join()