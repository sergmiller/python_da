import sys


class Rational(object):
    class RationalError(Exception):
        pass

    @staticmethod
    def gcd(x, y):
        while x:
            y, x = x, y % x
        return y

    def __init__(self, x=0, y=1):
        try:
            g = Rational.gcd(x, y)
            x //= g
            y //= g
        except ZeroDivisionError as e:
            raise RationalError('something wrong')

        if y < 0:
            x, y = -x, -y

        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x * other.y == self.y * other.x

    def __ne__(self, other):
        return not self == other

    def __str__(self):
        return str(self.x) + '/' + str(self.y)

    def __add__(self, other):
        return Rational(self.x * other.y + self.y * other.x, self.y * other.y)

    def __neg__(self):
        return Rational(-self.x, self.y)

    def __sub__(self, other):
        return self + (-other)

    def __mul__(self, other):
        return Rational(self.x * other.x, self.y * other.y)

    def __truediv__(self, other):
        return Rational(self.x * other.y, self.y * other.x)


exec(sys.stdin.read())
