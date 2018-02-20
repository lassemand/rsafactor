import unittest
import numpy as np
import rsa

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
        (pubkey, privkey) = rsa.newkeys(32)
        sut = rsa_dixon_random_squares(pubkey.n, pubkey.e)
        (p, q) = sut.factorize()
        if p == privkey.q:
            p, q = q, p
        self.assertEqual(p, privkey.p)
        self.assertEqual(q, privkey.q)

if __name__ == '__main__':
    unittest.main()
