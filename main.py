from stepn.client import *

email = input("Enter user E-Mail:")
password = input("Enter user password:")

client = Client()
login = client.login(email, password, lambda: input("Enter Google authenticator code:"))

if login:
    print("Login successful!")

    searchParams = {
        "order": 2001,
        "chain": 103,
        "refresh": True,
        "search": '',
        "page": 1,
        "otd": '',
        "type": '',
        "gType": '',
        "quality": '',
        'level': 0,
        'bread': 0
    }

    response = client.run("orderlist", searchParams)
    print(response.text)
