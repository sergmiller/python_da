import unittest
from z2_1 import Rational

def _f(x):
    return 2*x

class TestRational(unittest.TestCase):
    def test_1(self):
        self.assertEqual(str(Rational(2)), '2/1')

    def test_2(self):
        self.assertEqual(str(Rational(3, 9)), '1/3')

    def test_3(self):
        self.assertEqual(str(Rational(1, 8) - Rational(1, 2)),'-3/8')

    def test_4(self):
        self.assertEqual(_f(1),2)
unittest.main()
