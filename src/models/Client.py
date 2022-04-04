from __future__ import annotations

import json
import websockets
from typing import Tuple

from src.models.Block import Block


class Client:

    MAX_CHUNK_SIZE = 100
    MINUTE_TO_MILLISECONDS = 60000

    def __init__(self) -> None:
        self.block        = Block()
        self.blocks       = []
        self.milliseconds = 0

    def extract_data(self, response: str) -> Tuple[int, int]:
        data = json.loads(response)

        index = data.get('a')
        number = data.get('b')

        self.block.process(index, number)

        return (index, number)

    def verify_chunk_size(self, index: int) -> Client:
        if index == self.MAX_CHUNK_SIZE:
            self.blocks.append(self.block)
            self.block = Block()

        return self

    def print_blocks(self):
        text = 'Start info from last minute'
        print(text.center(50, '-'))

        for block in self.blocks:
            json_str = json.dumps(block.__dict__, indent = 2)
            print(json_str)

        text = 'Finish info from last minute'
        print(text.center(50, '-'))

    def verify_elapsed_time(self) -> Client:
        if self.milliseconds % self.MINUTE_TO_MILLISECONDS == 0:
            self.print_blocks()

            self.blocks = []

        return self

    def process(self, response: str) -> None:
        index, number = self.extract_data(response)

        self.verify_chunk_size(index)

        self.verify_elapsed_time()

    async def run(self):
        url = 'ws://209.126.82.146:8080'

        print('Conecting...')
        async with websockets.connect(url, ping_interval = None) as websocket:
            print('Conected.')
            print('Waiting for the first minute...')

            self.milliseconds = 1

            while True:
                response = await websocket.recv()

                # threading.Thread(target=self.extract_data, args=(response,)).start()
                self.process(response)

                self.milliseconds += 1
