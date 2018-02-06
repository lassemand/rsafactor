import unittest
import rsa

from factorizer.rsa_brent_pollard_rho import rsa_brent_pollard_rho
from factorizer.rsa_brute_force import rsa_brute_force
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

if __name__ == '__main__':
    unittest.main()
