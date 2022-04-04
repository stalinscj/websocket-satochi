import asyncio

from src.models.Client import Client

def main():
    client = Client()
    asyncio.run(client.run())

if __name__ == '__main__':
    main()
