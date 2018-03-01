import unittest

import numpy as np
import rsa
from interface import implements
from multiprocessing import Queue

from factorizer.dixon_random_squares.dixon_congruence_validator import dixon_congruence_validator
from factorizer.dixon_random_squares.rsa_dixon_random_squares import rsa_dixon_random_squares, find_next_selection
from factorizer.dixon_random_squares.rsa_dixon_random_squares_parallel import build_up_test_values
from factorizer.dixon_random_squares.rsa_dixon_random_squares_validate_congruence import \
    rsa_dixon_random_squares_test_congruence


class rsa_dixon_random_square_test(unittest.TestCase):
    def test_find_next_selection(self):
        pointers = [1, 0]
        selection, pointers = find_next_selection(np.array([2, 3, 4]), pointers)
        self.assertEqual(selection[0], 3)
        self.assertEqual(selection[1], 2)
        selection, pointers = find_next_selection(np.array([2, 3, 4]), pointers)
        self.assertEqual(selection[0], 4)
        self.assertEqual(selection[1], 2)
        selection, pointers = find_next_selection(np.array([2, 3, 4]), pointers)
        self.assertEqual(selection[0], 4)
        self.assertEqual(selection[1], 3)
        selection, pointers = find_next_selection(np.array([2, 3, 4]), pointers)
        self.assertEqual(selection, [])

    def test_dixon_random_squares_with_rsa_gen(self):
        (pubkey, privkey) = rsa.newkeys(32)
        sut = rsa_dixon_random_squares(pubkey.n, pubkey.e, rsa_dixon_random_squares_test_congruence())
        (p, q) = sut.factorize()
        if p == privkey.q:
            p, q = q, p
        self.assertEqual(p, privkey.p)
        self.assertEqual(q, privkey.q)

    def test_dixon_random_squares_with_book_example(self):
        sut = rsa_dixon_random_squares(713, 1, rsa_dixon_random_squares_test_congruence())
        (p, q) = sut.factorize()
        if p == 31:
            p, q = 23, 31
        self.assertEqual(p, 23)
        self.assertEqual(q, 31)

    def validate_even_number_used(self, ones, forced_ones):
        for one in ones:
            list = [o for o in one if o in forced_ones]
            if len(list) % 2 == 1:
                return False
        return True

    def test_build_up_test_values(self):
        queue = Queue()
        build_up_test_values(1, 77, 3, np.array([2, 3, 5, 7]), queue)
        Z, rows_in_factor = queue.get()
        self.assertEqual(3, len(Z))
        self.assertEqual(3, len(rows_in_factor))


if __name__ == '__main__':
    unittest.main()


class fake_validator(implements(dixon_congruence_validator)):
    def validate(self, forced_ones, Z, all_rows_in_factor, B, n):
        self.forced_ones = forced_ones
        return 3, 5
