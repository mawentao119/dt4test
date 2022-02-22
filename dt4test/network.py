
import numpy as np


class Network:
    """
    网络服务的公共库.
    Numbers will be multiplied by the given multiplier.

    :param multiplier: 参数因子.
    :type multiplier: int
    """

    def __init__(self, multiplier):
        self.multiplier = multiplier

    def multiply(self, number):
        """
        Multiply a given number by the multiplier.

        :param number: The number to multiply.
        :type number: int

        :return: The result of the multiplication.
        :rtype: int
        """

        return np.dot(number, self.multiplier)
