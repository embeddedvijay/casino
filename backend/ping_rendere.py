import time , urllib.request
URL = "https://casino-backend-1mye.onrender.com/ping"

while True:
    try:
        with urllib.request.urlopen(URL) as res:
            data = res.read().decode('utf-8')
            print(f"Ping: {data}")
    except Exception as e:
        print(f"Error: {e}")
    time.sleep(240)