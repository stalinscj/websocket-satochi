from __future__ import annotations

import json
import time
import threading
import websockets
from typing import Tuple

from src.models.Block import Block


class Client:

    MAX_BLOCKS = 100
    MINUTE_TO_SECONDS = 60

    def __init__(self) -> None:
        self.blocks     = [ Block() for _ in range(self.MAX_BLOCKS) ]
        self.start_time = None
        self.processing = False

    def extract_data(self, response: str) -> Tuple[int, int]:
        data = json.loads(response)

        index  = data.get('a')
        number = data.get('b')

        return (index, number)

    def print_blocks(self):
        text = 'Start info from last minute'
        print(text.center(50, '-'))

        for block in self.blocks:
            json_str = json.dumps(block.__dict__, indent = 2)
            print(json_str)

        text = 'Finish info from last minute'
        print(text.center(50, '-'))

    def reset_blocks(self) -> Client:
        for block in self.blocks:
            block.__dict__ = Block().__dict__

        return self

    def verify_elapsed_time(self) -> Client:
        current_time = time.time()
        elapsed_time = current_time - self.start_time

        if elapsed_time > self.MINUTE_TO_SECONDS:
            while self.processing:
                ...

            self.print_blocks()

            self.start_time = current_time

            self.reset_blocks()

        return self

    def process(self, response: str) -> threading.Thread:
        index, number = self.extract_data(response)

        block = self.blocks[index - 1]

        self.verify_elapsed_time()

        thread = threading.Thread(target = block.process, args = (number, self))

        thread.start()

        return thread

    async def run(self):
        url = 'ws://209.126.82.146:8080'

        print('Conecting...')
        async with websockets.connect(url, ping_interval = None) as websocket:
            print('Conected.')
            print('Waiting for the first minute...')

            self.start_time = time.time()

            while True:
                response = await websocket.recv()

                self.process(response)
