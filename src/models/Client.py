from __future__ import annotations

import json
import time
import websockets
from typing import Tuple
from collections import deque
from threading import Event, Thread

from src.models.Block import Block


class Client:

    MAX_THREADS       = 3
    MAX_BLOCKS        = 100
    MINUTE_TO_SECONDS = 60
    QUEUE_PREFIX_NAME = 'queue_'
    HOST              = '209.126.82.146'
    PORT              = 8080

    def __init__(self, host: str = None, port: int = None) -> None:
        self.blocks  = [ Block() for _ in range(self.MAX_BLOCKS) ]
        self.threads = {}
        self.queues  = self.create_queues()
        self.dequeues_counter  = self.create_dequeues_counter()

        self.enqueued          = Event()
        self.queues_idle       = Event()
        self.thread_finished   = Event()
        self.blocks_rebooted   = Event()
        self.waiting_for_reset = False

        self.host = host or self.HOST
        self.port = port or self.PORT

    def create_queues(self):
        queues = {}

        for i in range(1, self.MAX_BLOCKS + 1):
            queue_name = self.QUEUE_PREFIX_NAME + str(i)

            queues[queue_name] = deque()

        return queues

    def create_dequeues_counter(self):
        dequeues_counter = {}

        for i in range(1, self.MAX_BLOCKS + 1):
            queue_name = self.QUEUE_PREFIX_NAME + str(i)

            dequeues_counter[queue_name] = 0

        return dequeues_counter

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

        self.blocks_rebooted.set()

        return self

    def wait_threads_finished(self):
        threads = list(self.threads.values())
        for thread in threads:
            try:
                if thread.is_alive():
                    thread.join()
            except Exception:
                pass

    def print_reset_worker(self):
        while True:
            time.sleep(self.MINUTE_TO_SECONDS)

            self.blocks_rebooted.clear()

            self.wait_threads_finished()

            self.print_blocks()

            self.reset_blocks()

    def enqueue(self, index: int, number: int) -> deque[Tuple[int, int]]:
        queue_name = self.QUEUE_PREFIX_NAME + str(index)

        self.queues_idle.wait()

        queue = self.queues.get(queue_name)

        queue.append((index, number))

        self.queues_idle.set()
        self.enqueued.set()

        return queue

    def process(self, response: str):
        index, number = self.extract_data(response)

        self.enqueue(index, number)


    def are_queues_empty(self) -> bool:
        empty = True

        self.queues_idle.wait()

        for queue in self.queues.values():
            if len(queue) > 0:
                empty = False
                break

        self.queues_idle.set()

        return empty

    def get_queue_to_process(self) -> deque[Tuple[int, int]] | None:
        queue_names = sorted(self.dequeues_counter, key=self.dequeues_counter.get)

        queue_to_process = None

        for queue_name in queue_names:

            if not queue_name in self.threads:
                self.queues_idle.wait()

                queue = self.queues[queue_name]

                if len(queue) > 0:
                    queue_to_process = queue
                    break

        self.queues_idle.set()

        return queue_to_process

    def dequeue(self, queue: deque[Tuple[int, int]]) -> Tuple(int, int):
        self.queues_idle.wait()

        index, number = queue.popleft()

        self.queues_idle.set()

        queue_name = self.QUEUE_PREFIX_NAME + str(index)

        self.dequeues_counter[queue_name] += 1

        return (index, number)

    def lauch_processing_thread(self, index: int, number: int) -> Thread:
        block = self.blocks[index - 1]

        thread_name = self.QUEUE_PREFIX_NAME + str(index)

        thread = Thread(
            name   = thread_name,
            target = block.process,
            args   = (number, thread_name, self)
        )

        self.threads[thread_name] = thread

        thread.start()

        return thread

    def worker(self):
        while True:
            if self.are_queues_empty():
                self.enqueued.wait()
                self.enqueued.clear()

            self.thread_finished.clear()
            if len(self.threads) >= self.MAX_THREADS:
                self.thread_finished.wait()

            self.blocks_rebooted.wait()

            queue = self.get_queue_to_process()

            if queue:
                index, number = self.dequeue(queue)

                self.lauch_processing_thread(index, number)
            elif self.threads:
                self.thread_finished.wait()

    async def run(self):
        url = f'ws://{self.host}:{self.port}'

        print('Conecting...')
        async with websockets.connect(url, ping_interval = None) as websocket:
            print('Conected.')
            print('Waiting for the first minute...')

            self.blocks_rebooted.set()
            self.queues_idle.set()

            Thread(target = self.worker).start()
            Thread(target = self.print_reset_worker).start()

            while True:
                response = await websocket.recv()

                self.process(response)
