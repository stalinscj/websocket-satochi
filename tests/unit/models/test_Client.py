import time
from random import randint

from src.models.Block import Block
from src.models.Client import Client


class TestClient:

    def test_new_clients_must_be_initialized(self):
        new_client = Client()

        assert new_client.start_time == None
        assert new_client.processing == False
        assert isinstance(new_client.blocks, list)
        assert len(new_client.blocks) == Client.MAX_BLOCKS

        for block in new_client.blocks:
            assert isinstance(block, Block)

    def test_extract_data(self, mocker):
        client = Client()

        index  = randint(1, Client.MAX_BLOCKS)
        number = randint(0, 1000)

        response = f'{{ "a": {index}, "b": {number} }}'

        assert (index, number) == client.extract_data(response)

    def test_verify_elapsed_time(self, mocker):
        client = Client()

        blockA = Block()
        blockA.first_number = 1

        blockB = Block()
        blockB.last_number = 10

        blocks = [blockA, blockB]
        client.blocks = blocks

        client.start_time = time.time()

        print_blocks_mock = mocker.patch.object(client, 'print_blocks')

        client = client.verify_elapsed_time()

        assert client.blocks == blocks
        assert client.blocks[0].__dict__ == blockA.__dict__
        assert client.blocks[1].__dict__ == blockB.__dict__
        print_blocks_mock.assert_not_called()

        client.start_time -= Client.MINUTE_TO_SECONDS
        client = client.verify_elapsed_time()

        assert client.blocks == blocks
        assert client.blocks[0].__dict__ == Block().__dict__
        assert client.blocks[1].__dict__ == Block().__dict__
        print_blocks_mock.assert_called_once()

    def test_print_blocks(self, mocker):
        client = Client()

        json_dumps_mock = mocker.patch('json.dumps')

        client.print_blocks()
        json_dumps_mock.assert_called_with(Block().__dict__, indent = 2)

        block = Block()
        block.first_number = 1

        client.blocks    = client.blocks[:1]
        client.blocks[0] = block

        client.print_blocks()
        json_dumps_mock.assert_called_with(block.__dict__, indent = 2)

    def test_reset_blocks(self):
        client = Client()

        blocks = client.blocks

        for block in client.blocks:
            block.first_number = randint(0, 1000)
            block.last_number  = randint(250, 500)

        client.reset_blocks()

        assert blocks == client.blocks

        new_block = Block()
        for block in client.blocks:
            assert block.__dict__ == new_block.__dict__


    def test_process(self, mocker):
        client = Client()
        client.start_time = time.time()

        verify_elapsed_time_mock = mocker.patch.object(client, 'verify_elapsed_time')

        index  = randint(1, Client.MAX_BLOCKS)
        number = randint(0, 1000)

        block = client.blocks[index - 1]
        block_process_mock = mocker.patch.object(block, 'process')

        response = f'{{ "a": {index}, "b": {number} }}'

        thread = client.process(response)

        thread.join()

        block_process_mock.assert_called_once_with(number, client)
        verify_elapsed_time_mock.assert_called_once()
