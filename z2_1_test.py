import unittest
from z2_1 import Rational

class TestRational(unittest.TestCase):
 def test_1(self):
     self.assertEqual(str(Rational(2)), '2/1')

 def test_2(self):
     self.assertEqual(str(Rational(3, 9)), '1/3')

 def test_3(self):
     self.assertEqual(str(Rational(1, 8) - Rational(1, 2)),'-3/8')

unittest.main()
