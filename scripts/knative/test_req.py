import os
import random
from uuid import uuid4

import requests

ip = os.getenv("LOAD_BALANCER_IP")
print(ip)


def main():
    user_index = random.randint(0, 99)
    username = f"username_{user_index}"
    password = f"password_{user_index}"
    title = "Aquaman"
    rating = random.randint(1, 9)
    text = "This is a review"
    headers = {"Content-Type": "application/json",
               "Host": "frontend.default.example.com"}
    r = requests.post(f"http://{ip}/compose", json={
        "args": [username, password, title, rating, text],
        "req_id": str(uuid4())
    }, headers=headers)
    print(r.json())


if __name__ == '__main__':
    main()
