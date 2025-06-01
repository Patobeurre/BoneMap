import numpy as np

HEIGHT = 300
WIDTH = 360

class MapMask:

    def __initDefault(self, size=(HEIGHT, WIDTH)):
        shape = size
        self.map = np.zeros(shape)
        self.mask = np.zeros(HEIGHT)
        self.min = 0
        self.max = 0

    def __init__(self, size=(HEIGHT, WIDTH), map=None, clean=False):
        if map is None:
            self.__initDefault()
        else:
            self.setMap(map)

    def updateMask(self):
        col = np.copy(self.map[:,0])
        col[~np.isnan(col)] = 1
        col[np.isnan(col)] = 0
        self.mask = col

    def flip(self, axis=0):
        if axis == 0:
            self.map = np.flipud(self.map)
            self.mask = np.flip(self.mask)
        elif axis == 1:
            self.map = np.fliplr(self.map)

    def shift(self, value :int, axis=1):
        self.map = np.roll(self.map, value, axis=axis)

    def cleanMap(self):
        for row in self.map:
            row[np.isnan(row)] = 0

    def computeMinMax(self):
        arr = self.getMapTrueData()
        if not arr.any(): return
        self.min = np.min(arr)
        self.max = np.max(arr)

    def setMap(self, newMap):
        self.map = newMap
        self.updateMask()
        self.computeMinMax()

    def getMapTrueData(self):
        arr = [self.map[i] for i in range(len(self.map)) if self.mask[i] > 0]
        return np.array(arr)

    def getNormMinMax(self, customMin=0, customMax=1):
        self.computeMinMax()
        norm = ((self.map - self.min) * ((customMax - customMin) / (self.max - self.min))) + customMin
        normMap = MapMask(map=norm)
        normMap.mask = self.mask
        return normMap

    def getNormMMAD(self):
        mmadMapMask = MapMask(map=np.copy(self.map))
        mmadMapMask.mask = self.mask

        values = self.getMapTrueData().flatten()

        med = np.median(values)
        mad = median_absolute_deviation(values)

        mmadMapMask.map -= med
        mmadMapMask.map /= (b * mad)

        mmadMapMask.computeMinMax()

        return mmadMapMask

    def getNormAvg(self):
        avgMap = MapMask(map=np.copy(self.map))
        avgMap.mask = self.mask

        arr = self.getMapTrueData().flatten()
        ave = np.average(arr)
        avgMap.map /= ave

        return avgMap

    def __truediv__(self, factor :float):
        for i in range(len(self.mask)):
            if self.mask[i] > 0:
                div = [x / factor for x in self.map[i]]
                self.map[i] = div

    def merge(self, other):
        for i in range(len(other.mask)):
            if other.mask[i] > 0:
                self.map[i] = other.map[i]
                self.mask[i] = 1
