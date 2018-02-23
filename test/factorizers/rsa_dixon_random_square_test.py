import unittest
import numpy as np
import rsa

from factorizer.rsa_dixon_random_squares import rsa_dixon_random_squares, find_next_selection


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
        sut = rsa_dixon_random_squares(pubkey.n, pubkey.e)
        (p, q) = sut.factorize()
        if p == privkey.q:
            p, q = q, p
        self.assertEqual(p, privkey.p)
        self.assertEqual(q, privkey.q)

    def test_dixon_random_squares_with_book_example(self):
        sut = rsa_dixon_random_squares(713, 1)
        (p, q) = sut.factorize()
        if p == 31:
            p, q = 23, 31
        self.assertEqual(p, 23)
        self.assertEqual(q, 31)

    def test_dixon_random_squares_with_hard_ones(self):
        sut = rsa_dixon_random_squares(713, 1)
        ones = np.array([[2, 3], [4, 0], [4, 3, 0]])
        sut.factor_from_reduced_matrix(ones)

if __name__ == '__main__':
    unittest.main()
