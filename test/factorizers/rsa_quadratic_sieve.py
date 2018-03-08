import unittest

from helper.cryptographic_methods import sqrt_int, modular_square_root


class TestQuadraticSieve(unittest.TestCase):
    def test_sqrt(self):
        value = sqrt_int(17)
        self.assertEqual(4, value)

    def test_sqrt_mod_prime(self):
        result = modular_square_root(72, 607)
        self.assertEqual(50, result)

if __name__ == '__main__':
    unittest.main()
