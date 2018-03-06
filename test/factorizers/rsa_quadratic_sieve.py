import unittest

from helper.cryptographic_methods import sqrt_int


class TestQuadraticSieve(unittest.TestCase):
    def test_sqrt(self):
        value = sqrt_int(17)
        self.assertEqual(4, value)


if __name__ == '__main__':
    unittest.main()
