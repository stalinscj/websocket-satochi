import asyncio
import argparse

from src.models.Client import Client


def main():
    parser = argparse.ArgumentParser(description='Help TOM')

    parser.add_argument('--host', help="WS host", type=str)
    parser.add_argument('--port', help="WS port", type=int)

    args = parser.parse_args()

    host = args.host
    port = args.port

    client = Client(host, port)

    asyncio.run(client.run())

if __name__ == '__main__':
    main()
