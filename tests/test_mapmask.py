from mapmask import MapMask
import numpy as np
import unittest


class TestMapMask(unittest.TestCase):

    def setUp(self):
        map = np.array([ [2.0,1,5], \
                [3,-5,-6], \
                [6,4,3]])

        self.mapMask = MapMask(map=map)


    def test_getNormMinMax(self):
        normMap = self.mapMask.getNormMinMax(-2,2)
        #TODO
        print(normMap.map)

    def test_getNormAvg(self):
        avgMap = self.mapMask.getNormAvg()
        print(avgMap.map)

    def test_flip(self):
        self.mapMask.mask = np.array([0,0,1])
        self.mapMask.flip(0)
        print(self.mapMask.map)
        print(self.mapMask.mask)

    def test_shift(self):
        print(self.mapMask.map)
        self.mapMask.shift(1)
        print(self.mapMask.map)
