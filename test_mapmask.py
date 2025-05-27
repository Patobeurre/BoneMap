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
