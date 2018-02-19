import unittest
import numpy as np

from factorizer.rsa_dixon_random_squares import rsa_dixon_random_squares, find_next_selection


class rsa_dixon_random_square_test(unittest.TestCase):

    def test_find_next_selection(self):
        pointers = [1, 0]
        selection = find_next_selection(np.array([2, 3, 4]), pointers)
        self.assertEqual(selection[0], 3)
        self.assertEqual(selection[1], 2)
        selection = find_next_selection(np.array([2, 3, 4]), pointers)
        self.assertEqual(selection[0], 4)
        self.assertEqual(selection[1], 2)
        selection = find_next_selection(np.array([2, 3, 4]), pointers)
        self.assertEqual(selection[0], 4)
        self.assertEqual(selection[1], 3)
        selection = find_next_selection(np.array([2, 3, 4]), pointers)
        self.assertIsNone(selection)

    def test_dixon_random_squares_with_book_example(self):
        sut = rsa_dixon_random_squares(77, 1)
        (p, q) = sut.factorize()
        if p == 11:
            p, q = 7, 11
        self.assertEqual(p, 7)
        self.assertEqual(q, 11)

if __name__ == '__main__':
    unittest.main()
