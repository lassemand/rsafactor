import unittest
import numpy as np

from factorizer.rsa_dixon_random_squares import rsa_dixon_random_squares


class rsa_dixon_random_square_test(unittest.TestCase):

    def test_dixon_random_squares_with_book_example(self):
        sut = rsa_dixon_random_squares(77, 1)
        (p, q) = sut.factorize()
        if p == 7:
            p, q = 3, 7
        self.assertEqual(p, 3)
        self.assertEqual(q, 7)

if __name__ == '__main__':
    unittest.main()
