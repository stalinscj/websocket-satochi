import math
from random import randint

from src.models.Block import Block
from src.models.Client import Client


class TestBlock:

    def test_new_blocks_must_be_initialized(self):
        new_block = Block()

        assert new_block.max_number              == -math.inf
        assert new_block.min_number              == math.inf
        assert new_block.first_number            == None
        assert new_block.last_number             == None
        assert new_block.number_of_prime_numbers == 0
        assert new_block.number_of_even_numbers  == 0
        assert new_block.number_of_odd_numbers   == 0

    def test_is_first_number(self):
        block = Block()

        assert block.is_first_number() == True

        block.first_number = randint(1, 100)

        assert block.is_first_number() == False

    def test_is_min_number(self):
        block = Block()

        assert block.is_min_number(5) == True

        block.min_number = 5
        assert block.is_min_number(randint(6, 100)) == False
        assert block.is_min_number(randint(1, 4)) == True

    def test_is_max_number(self):
        block = Block()

        assert block.is_max_number(5) == True

        block.max_number = 5
        assert block.is_max_number(randint(1, 4)) == False
        assert block.is_max_number(randint(6, 100)) == True

    def test_is_odd_number(self):
        block = Block()

        odd_number  = 2 * randint(1, 100) + 1
        even_number = 2 * randint(1, 100)

        assert block.is_odd_number(odd_number) == True
        assert block.is_odd_number(even_number) == False

    def test_process(self):
        block = Block()
        client = Client()

        block = block.process(10, client)
        assert block.max_number == 10
        assert block.min_number == 10
        assert block.first_number == 10
        assert block.last_number == 10
        assert block.number_of_prime_numbers == 0
        assert block.number_of_even_numbers == 1
        assert block.number_of_odd_numbers == 0
        assert client.processing == False

        client.processing = True
        block = block.process(3, client)
        assert block.max_number == 10
        assert block.min_number == 3
        assert block.first_number == 10
        assert block.last_number == 3
        assert block.number_of_prime_numbers == 1
        assert block.number_of_even_numbers == 1
        assert block.number_of_odd_numbers == 1
        assert client.processing == False

        block = block.process(8, client)
        assert block.max_number == 10
        assert block.min_number == 3
        assert block.first_number == 10
        assert block.last_number == 8
        assert block.number_of_prime_numbers == 1
        assert block.number_of_even_numbers == 2
        assert block.number_of_odd_numbers == 1

        block = block.process(2, client)
        assert block.max_number == 10
        assert block.min_number == 2
        assert block.first_number == 10
        assert block.last_number == 2
        assert block.number_of_prime_numbers == 2
        assert block.number_of_even_numbers == 3
        assert block.number_of_odd_numbers == 1
