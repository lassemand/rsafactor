import unittest
import rsa
import numpy as np

from factorizer.rsa_brent_pollard_rho import rsa_brent_pollard_rho
from factorizer.rsa_brute_force import rsa_brute_force
from factorizer.rsa_dixon_random_squares import rsa_dixon_random_squares, find_all_pair_of_size, \
    find_set_to_reach_zero_sum_vector_from_candidates
from factorizer.rsa_pollard_rho import rsa_pollard_rho




class TestFactorizer(unittest.TestCase):
    def test_factorizer(self):
        (pubkey, privkey) = rsa.newkeys(32)
        sut = rsa_brute_force(pubkey.n, pubkey.e)
        (p, q) = sut.factorize()
        if p == privkey.q:
            temp = p
            p = q
            q = temp
        self.assertEqual(p, privkey.p)
        self.assertEqual(q, privkey.q)

    def test_pollard_rho(self):
        (pubkey, privkey) = rsa.newkeys(32)
        sut = rsa_pollard_rho(pubkey.n, pubkey.e)
        (p, q) = sut.factorize()
        if p == privkey.q:
            temp = p
            p = q
            q = temp
        self.assertEqual(p, privkey.p)
        self.assertEqual(q, privkey.q)

    def test_brent_pollard_rho(self):
        (pubkey, privkey) = rsa.newkeys(32)
        sut = rsa_brent_pollard_rho(pubkey.n, pubkey.e)
        (p, q) = sut.factorize()
        if p == privkey.q:
            temp = p
            p = q
            q = temp
        self.assertEqual(p, privkey.p)
        self.assertEqual(q, privkey.q)

    def test_brent_pollard_rho(self):
        sut = rsa_dixon_random_squares(123123123, 1)
        (p, q) = sut.factorize()

    def test_all_pairs_of_given_length(self):
        result = find_all_pair_of_size(5,3)
        self.assertEqual(len(result), 10)


    def test_zero_sum_vector_candidates(self):
        matrix = np.matrix([[1, 0, 0, 1, 0, 0, 1], [0, 0, 0, 1, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0], [1, 0, 0, 0, 0, 1, 0], [1, 0, 0, 0, 1, 0, 1], [0, 0, 0, 1, 0, 0, 0], ])
        result =  find_set_to_reach_zero_sum_vector_from_candidates(matrix, find_all_pair_of_size(6, 4))
        self.assertEqual(len(result), 2)

if __name__ == '__main__':
    unittest.main()
