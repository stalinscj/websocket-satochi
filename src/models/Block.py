from __future__ import annotations

import math
import sympy


class Block:

    def __init__(self) -> None:
        self.max_number              = -math.inf
        self.min_number              = math.inf
        self.first_number            = None
        self.last_number             = None
        self.number_of_prime_numbers = 0
        self.number_of_even_numbers  = 0
        self.number_of_odd_numbers   = 0

    def is_first_number(self) -> bool:
        return self.first_number is None

    def is_min_number(self, number: int) -> bool:
        return True if number < self.min_number else False

    def is_max_number(self, number: int) -> bool:
        return True if number > self.max_number else False

    def is_odd_number(self, number: int) -> bool:
        return True if number % 2 else False

    def process(self, number: int, client) -> Block:
        client.processing = True

        self.last_number = number

        if self.is_first_number():
            self.first_number = number

        if self.is_min_number(number):
            self.min_number = number

        if self.is_max_number(number):
            self.max_number = number

        if sympy.isprime(number):
            self.number_of_prime_numbers += 1

        if self.is_odd_number(number):
            self.number_of_odd_numbers += 1
        else:
            self.number_of_even_numbers += 1

        client.processing = False

        return self
