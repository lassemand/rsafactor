import unittest
import numpy as np

from factorizer.rsa_dixon_random_squares import rsa_dixon_random_squares


class rsa_dixon_random_square_test(unittest.TestCase):

    def test_find_next_selection(self):
        selection = find_next_selection([[2, 3, 4], [0, 1]])
        self.assertEqual(p, 7)
        self.assertEqual(q, 11)

    def test_dixon_random_squares_with_book_example(self):
        sut = rsa_dixon_random_squares(77, 1)
        (p, q) = sut.factorize()
        if p == 11:
            p, q = 7, 11
        self.assertEqual(p, 7)
        self.assertEqual(q, 11)

if __name__ == '__main__':
    unittest.main()
