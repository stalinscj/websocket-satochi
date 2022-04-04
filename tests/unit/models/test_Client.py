from random import randint

from src.models.Block import Block
from src.models.Client import Client


class TestClient:

    def test_new_clients_must_be_initialized(self):
        new_client = Client()

        assert new_client.block.__dict__ == Block().__dict__
        assert new_client.blocks         == []
        assert new_client.milliseconds   == 0

    def test_extract_data(self, mocker):
        client = Client()

        index  = randint(1, 100)
        number = randint(0, 1000)

        response = f'{{ "a": {index}, "b": {number} }}'

        process_mock = mocker.patch.object(client.block, 'process')

        assert (index, number) == client.extract_data(response)

        process_mock.assert_called_once_with(index, number)

    def test_verify_chunk_size(self):
        client = Client()
        block = client.block

        index  = randint(1, Client.MAX_CHUNK_SIZE - 1)

        client = client.verify_chunk_size(index)
        assert len(client.blocks) == 0
        assert block == client.block

        client = client.verify_chunk_size(Client.MAX_CHUNK_SIZE)
        assert len(client.blocks) == 1
        assert block != client.block

    def test_verify_elapsed_time(self, mocker):
        client = Client()
        blocks = [Block(), Block()]
        client.blocks = blocks
        client.milliseconds = randint(1, Client.MINUTE_TO_MILLISECONDS)

        print_blocks_mock = mocker.patch.object(client, 'print_blocks')

        client = client.verify_elapsed_time()

        assert client.blocks == blocks
        print_blocks_mock.assert_not_called()

        client.milliseconds = Client.MINUTE_TO_MILLISECONDS
        client = client.verify_elapsed_time()

        assert client.blocks == []
        print_blocks_mock.assert_called_once()

    def test_print_blocks(self, mocker):
        client = Client()

        json_dumps_mock = mocker.patch('json.dumps')

        client.print_blocks()
        json_dumps_mock.assert_not_called()


        block = Block()
        client.blocks = [block, Block()]

        client.print_blocks()
        json_dumps_mock.assert_called_with(block.__dict__, indent = 2)
