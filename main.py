from stepn.util import login
from stepn.client import Client

if __name__ == '__main__':
    client = Client()
    if login(client, False):
        print("Logged in!")
