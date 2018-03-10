import unittest

import rsa
from factorizer.dixon_random_squares.rsa_dixon_random_squares import rsa_dixon_random_squares
from factorizer.dixon_random_squares.rsa_dixon_random_squares_validate_congruence import \
    rsa_dixon_random_squares_test_congruence


class rsa_dixon_random_square_test(unittest.TestCase):

    def test_dixon_random_squares(self):
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

if __name__ == '__main__':
    unittest.main()


