from core import opencv_utils as cvutil
from utils import *
import unittest

class TestOpencvUtils(unittest.TestCase):

    def setUp(self):
        print("setup")


    def test_getNearestPoint(self):
        a = Point(1,1)
        b = Point(-1,5)
        c = Point(2,3)

        vec = np.array([a, b, c])

        pointToTest = Point(2,4)

        nearestPoint = cvutil.getNearestPoint(pointToTest, vec)
        print(pointToTest)
        print(nearestPoint)


    def test_ICH(self):
        cvutil.testICH()
