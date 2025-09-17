import os
import shutil
import cv2
import numpy as np
from mapmask import MapMask


def importMap(filepath):
    map = np.genfromtxt(filepath, delimiter=' ')
    return MapMask(map)

def exportMap(mapMask, filepath):
    arr = np.empty(mapMask.map.shape, dtype=object)

    for i in range(len(mapMask.mask)):
        if mapMask.mask[i] > 0:
            arr[i] = ["%.8f" % number for number in mapMask.map[i]]
        else:
            arr[i] = ['none' for x in range(len(mapMask.map[i]))]

    np.savetxt(filepath, arr, delimiter=" ", fmt="%s")


import matplotlib.pyplot as plt
from matplotlib import cm


def plot_colorMap(data, min=None, max=None):
    cms = cm.get_cmap('jet', 256)

    if min is None:
        min = np.min(np.ma.masked_array(data, np.isnan(data)))
    if max is None:
        max = np.max(np.ma.masked_array(data, np.isnan(data)))

    fig, axs = plt.subplots(1, 1, figsize=(6, 5), constrained_layout=True)
    psm = axs.pcolormesh(data, cmap=cms, rasterized=True, vmin=min, vmax=max)
    fig.colorbar(psm, ax=axs)
    plt.show()


def showImageWindow(name :str, img):
    cv2.imshow(name, img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()


def generateResultMap (mapMask :MapMask, mapName :str, settings):

    mapMask.computeMinMax()
    print(str(mapMask.min) + ":" + str(mapMask.max))

    filePath = settings.OUTPUT_DIR_PATH + "/" + mapName + ".txt"

    exportMap(mapMask, filePath)

    if settings.bNormMinMax:
        filePath = settings.OUTPUT_DIR_PATH + "/" + mapName + "_norm.txt"
        normMap = mapMask.getNormMinMax(settings.customMin, settings.customMax)
        exportMap(normMap, filePath)

    if settings.bNormMMAD:
        filePath = settings.OUTPUT_DIR_PATH + "/" + mapName + "_mmad.txt"
        mmadMap = mapMask.getNormMMAD()
        exportMap(mmadMap, filePath)

        filePath = settings.OUTPUT_DIR_PATH + "/" + mapName + "_tanh.txt"
        mmadMap.map = np.tanh(mmadMap.map)
        exportMap(mmadMap, filePath)

    if settings.bNormAvg:
        filePath = settings.OUTPUT_DIR_PATH + "/" + mapName + "_avg.txt"
        avgMap = mapMask.getNormAvg()
        exportMap(avgMap, filePath)

    if settings.bBlur:
        ksize = (3, 10)
        cv2.blur(mapMask.map, ksize)

    plot_colorMap(mapMask.map, mapMask.min, mapMask.max)


def retreiveFilesInFolder(directory :str, extensionFilters):

    if not os.path.exists(directory): return

    filelist = []
    for dirpath,_,filenames in os.walk(directory):
        for file in filenames:
            if file.endswith(extensionFilters):
                filelist.append(os.path.abspath(os.path.join(dirpath, file)))

    return np.array(filelist)


def createFolder(dirPath :str, removeIfExists = False):
    if os.path.exists(dirPath) and removeIfExists:
        shutil.rmtree(dirPath)

    os.makedirs(dirPath)

    return


def copyFile(src :str, dst :str):
    shutil.copy(src, dst)


class Point:
    def __init__(self, x_init, y_init):
        self.x = x_init
        self.y = y_init

    def copy(self):
        return Point(self.x, self.y)

    def shift(self, x, y):
        self.x += x
        self.y += y

    def __sub__(self, other):
        self.x -= other.x
        self.y -= other.y

    def __eq__(self, other) -> bool:
        return (self.x == other.x and self.y == other.y)

    def __repr__(self):
        return "".join(["Point(", str(self.x), ",", str(self.y), ")"])

    def parse(s :str):
        if s.startswith("Point(") and s.endswith(")"):
            args = s[len("Point("):-1]  # Supprime "Point(" et ")"
            x_str, y_str = args.split(",")
            x = int(x_str.strip())
            y = int(y_str.strip())
            return Point(x, y)
        else:
            raise ValueError("Format non reconnu pour Point")


class PointB:
    def __init__(self, x=0, y=0, a=0, r=0):
        self.x = x
        self.y = y
        self.angle = a
        self.r = r

    def toSimplePoint(self):
        return Point(self.x, self.y)

    def __sub__(self, other):
        self.x -= other.x
        self.y -= other.y

    def __repr__(self):
        return "".join(["Point(", str(self.x), ",", str(self.y), " : ", str(self.r), ")"])
