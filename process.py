import cv2
import os
import numpy as np
import math
import time
from multiprocessing import Pool
from utils import *
from mapmask import MapMask
from math_interpreter import MathInterpreter
from data import *


# =====
# Erosion and dilation operations
# =====

def openSection (src: cv2.Mat, erosion_size: int, ite: int) -> cv2.Mat:
    """
    Apply erosion then dilation on the source image.
    Return the resulting image.
    """

    erosion_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        ( 2 * erosion_size + 1, 2 * erosion_size + 1 ),
        ( erosion_size, erosion_size ) )

    dilation_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        ( 2 * erosion_size + 1, 2 * erosion_size + 1 ),
        ( erosion_size, erosion_size ) )

    dst: cv2.Mat = src.copy()

    for i in range(ite):
        dst = cv2.erode(dst, erosion_kernel)

    for i in range(ite):
        dst = cv2.dilate(dst, dilation_kernel)

    return dst


def closeSection (src: cv2.Mat, erosion_size: int, ite: int) -> cv2.Mat:
    """
    Apply dilation then erosion on the source image.
    Return the resulting image.
    """

    erosion_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        ( 2 * erosion_size + 1, 2 * erosion_size + 1 ),
        ( erosion_size, erosion_size ) )

    dilation_kernel = cv2.getStructuringElement(
        cv2.MORPH_ELLIPSE,
        ( 2 * erosion_size + 1, 2 * erosion_size + 1 ),
        ( erosion_size, erosion_size ) )

    dst: cv2.Mat = src.copy()

    for i in range(ite):
        dst = cv2.dilate(dst, dilation_kernel)

    for i in range(ite):
        dst = cv2.erode(dst, erosion_kernel)

    return dst


def smooth (data: np.ndarray, it: int) -> np.ndarray:

    vec = np.zeros(len(data))

    for j in range(it):
        for i in range(len(data)):
            id1 = i-2
            id2 = i-1

            id3 = i+1
            id4 = i+2

            if id1 < 0:
                id1 = len(data) + id1
            if id2 < 0:
                id2 = len(data) + id2

            if id3 >= len(data):
                id3 = id3 - len(data)
            if id4 >= len(data):
                id4 = id4 - len(data)

            vec[i] = (7 * data[id1] +
                       26 * data[id2] +
                       41 * data[i] +
                       26 * data[id3] +
                       7 * data[id4]) / 107.0
    return vec


def getCenterOfSection(section :cv2.Mat) -> Point:
    """
    Compute the centroid of all points of a section.
    """

    y, x = np.where(section > 0)
    count :int = len(x)

    centroid = Point(int(np.sum(x)/count), int(np.sum(y)/count))

    return centroid


def rotateImage(image :cv2.Mat, angle :float, center :Point):
    """
    Rotate an image.
    """

    image_center = tuple([center.x, center.y])
    rot_mat = cv2.getRotationMatrix2D(image_center, angle, 1.0)
    result = cv2.warpAffine(image, rot_mat, image.shape[1::-1], flags=cv2.INTER_LINEAR)

    return result


def replaceImageValue(img :cv2.Mat, newVal :int):
    """
    Replace a value by another within an image.
    """

    img[img > 0] = newVal


def findBlobs(image :cv2.Mat):

    #image = cv2.imread("/home/patobeur/Bureau/marouflage.png", cv2.IMREAD_GRAYSCALE)
    params = cv2.SimpleBlobDetector_Params()

    params.filterByColor = True
    params.minThreshold = 0
    params.maxThreshold = 255

    detector = cv2.SimpleBlobDetector_create(params)
    keypoints = detector.detect(image)

    #blank = np.zeros((1, 1))
    #blobs = cv2.drawKeypoints(
    #    image, keypoints, blank, (0, 0, 255), cv2.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS
    #)

    #showImageWindow("Blobs Using Area", blobs)

    return keypoints


def computeExternalRadius(contours, centroid):

    vec :np.ndarray = []

    contourExt = np.copy(contours[0])

    for i in range(len(contourExt)):

        pc = contourExt[i].flatten()
        p :Point = Point(pc[0], pc[1])

        dist = float(cv2.norm(np.array([p.x - centroid.x, p.y - centroid.y])))

        vec.append(dist)

    return np.array(vec)


def computeCorticalThikness(contours):
    vec = []
    contourExt = np.copy(contours[0])
    contourInn = np.copy(contours[1])

    for pcExt in contourExt:
        min = 2000.0

        for pcInn in contourInn:
            d :float = float(cv2.norm(np.array([pcExt.flatten()[0] - pcInn.flatten()[0], pcExt.flatten()[1] - pcInn.flatten()[1]])))
            if (d < min):
                min = d

        vec.append(min)

    return np.array(vec)


def computeCurvature (radiusExt):

    res = np.copy(radiusExt)
    temp = np.copy(res)
    size :int = len(radiusExt)

    for j in range(2):

        for i in range(size):

            if (i == 0):
                res[i] = temp[size-1] * (-2.0) + temp[1] * 2.0
            elif (i == size-1):
                res[i] = temp[i-1] * (-2.0) + temp[0] * 2.0
            else:
                res[i] = temp[i-1] * (-2.0) + temp[i+1] * 2.0

        temp = np.copy(res)

    return res


def secondMoments (section :cv2.Mat, centroid, angle :float):

    angle = math.radians(angle)
    count :int = 0

    y, x = np.where(section > 0)

    for i in range(len(x)):
        p = Point((x[i] - centroid.x), (y[i] - centroid.y))
        p.y = int(-p.x * math.sin(angle) + p.y * math.cos(angle) + 0.5)
        count = count + 1 * p.y**2

    return count;



def computeSecondMoments (section :cv2.Mat, centroid, bRight, pixelSize :Point = Point(1,1)) -> np.ndarray:

    res = np.zeros(180)
    y, x = np.where(section > 0)
    y = [py - centroid.y for py in y]
    x = [px - centroid.x for px in x]

    for a in range(180):
        angle :float = 0.0

        if (bRight):
            angle = 360 - (a + 90)
        else:
            angle = a + 90
            if angle > 359:
                angle = angle - 360

        angle = math.radians(angle)
        val = 0
        for i in range(len(x)):
            py = int(-x[i] * math.sin(angle) + y[i] * math.cos(angle) + 0.5)
            val = val + py**2

        res[a] = val * float(pixelSize.x)**2 * float(pixelSize.y)**2

    return np.append(res, res)


def modulus (section :cv2.Mat, angle :float, moment :float, centroid, pixelSize :Point = Point(1,1)):

    rotatedMat = rotateImage(section, 360-angle, centroid)

    contours, hierarchy = cv2.findContours(rotatedMat, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    dymax :float = 0.0
    dymax2 :float = 0.0

    for i in range(len(contours[0])):

        pc = contours[0][i].flatten()
        p = Point(pc[0] - centroid.x, pc[1] - centroid.y)

        if p.x > dymax:
            dymax = p.x
        elif p.x < dymax2:
            dymax2 = p.x;

    dymax = dymax * float(pixelSize.x)
    dymax2 = dymax2 * float(pixelSize.y)

    dymax2 = abs(dymax2)

    moduli = moment / np.max([dymax, dymax2])
    moduliHalf = moment / dymax

    return moduli, moduliHalf


def computeModulus(section: cv2.Mat, moments, centroid, pixelSize :Point = Point(1,1)):

    resModuli = np.zeros(len(moments))
    resModuliHalf = np.zeros(len(moments))

    for i in range(len(moments)):
        moduli, moduliHalf = modulus(section, i, moments[i], centroid, pixelSize)

        resModuli[i] = moduli
        resModuliHalf[i] = moduliHalf

    return resModuli, resModuliHalf


def getContoursPointsWithAngles (section :cv2.Mat, contour :np.ndarray, centroid, values = []):

    if not len(values) > 0:
        values = np.zeros(len(contour))

    centroid.y = len(section) - centroid.y

    vec :np.ndarray = []

    for i in range(len(contour)):

        pc = contour[i][0]
        p :Point = Point(pc[0], pc[1])

        # transpose point to origin
        p.x -= centroid.x
        p.y = len(section) - p.y - centroid.y

        # get angle by trigonometry
        tetha = p.y / p.x
        a = math.atan(tetha)
        a = math.degrees(a)
        if p.x < 0:
            a += 180.0
        elif p.y < 0:
            a += 360.0

        # save point to list
        pb = PointB(p.x, p.y)
        pb.angle = a
        pb.r = values[i]
        vec.append(pb)

    vec.sort(key=lambda x: x.angle)

    return vec


def cartesianToPolar (section: cv2.Mat,
                      contours: np.ndarray,
                      values,
                      centroid,
                      bRight :bool = False) -> np.ndarray:

    res = np.zeros(360)

    vec = getContoursPointsWithAngles(section, contours[0], centroid.copy(), values)

    index = 0
    finished = False

    for i in range(360):

        angle = 0.0

        if bRight:
            angle = i
        else:
            angle = abs(i - 360) - 180
            if angle < 0:
                angle = 360 + angle

        if not finished:
            if i > vec[index].angle:
                while i > vec[index].angle:
                    index += 1
                    if index >= len(vec):
                        finished = True
                        break

        if index == 0:
            d = vec[index].angle + 360 - vec[len(vec)-1].angle
            t = (i + 360 - vec[len(vec)-1].angle) / d
            val = (1-t) * vec[len(vec)-1].r + vec[index].r*t

            res[int(angle)] = val
        else:
            if finished:
                d = vec[0].angle + 360 - vec[index-1].angle
                t = (i - vec[index-1].angle) / d
                val = (1-t) * vec[index-1].r + vec[0].r*t

                res[int(angle)] = val

            else:
                if i < vec[index].angle:
                    d = vec[index].angle - vec[index-1].angle
                    t = (i - vec[index-1].angle)/d
                    val = (1-t) * vec[index-1].r + vec[index].r*t

                    res[int(angle)] = val
                elif i == vec[index].angle:
                    val = vec[index].r

                    res[int(angle)] = val

    return res


def standardizeMat (mat :cv2.Mat, stand :float):

    for i, j in np.where(mat > 0):
        mat[i][j] /= stand


def reconstructImageSection (imagesSampled, index :int, settings) -> cv2.Mat:

    curImg = cv2.imread(imagesSampled[index], cv2.IMREAD_GRAYSCALE)

    replaceImageValue(curImg, settings.MASK_MAX)

    #showImageWindow("before close", curImg)
    curImg = closeSection(curImg, settings.EROSION_SIZE, settings.N_ITE)
    #showImageWindow(str(ind), curImg)

    return curImg


def launchThreadedProcess (imagesSampled, begin :int, end :int, settings, callback):

    mapCurv = MapMask((len(imagesSampled), 360))
    mapDist = MapMask((len(imagesSampled), 360))
    mapCort = MapMask((len(imagesSampled), 360))
    mapMoments = MapMask((len(imagesSampled), 360))
    mapMomentsJ = MapMask((len(imagesSampled), 360))
    mapMomentsZpol = MapMask((len(imagesSampled), 360))
    mapModulus = MapMask((len(imagesSampled), 360))
    mapModulusHalf = MapMask((len(imagesSampled), 360))

    for nImg in range(begin, end):

        ind :int = nImg
        if (ind < 0):
            ind = 0

        curImg = reconstructImageSection(imagesSampled, nImg, settings)

        centroid = getCenterOfSection(curImg)

        # Preparation of the image

        if (settings.bFlip):
            cv2.flip(curImg, 0)
        if (settings.bRotate):
            curImg = rotateImage(curImg, settings.sectionRotAngle, centroid)

        cv2.imwrite("/home/patobeur/Documents/BoneMap/BoneMap/BoneMap/reconstructedSerie/" + "sec_" + str(ind) + ".png", curImg)

        contours, heirarchy = cv2.findContours(curImg, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

        bValid = False
        if (len(contours) == 2):
            blobsCount = findBlobs(curImg)
            #if (len(blobsCount) == 1):
            bValid = True


        mapDist.mask[ind] = int(bValid)
        mapCort.mask[ind] = int(bValid)
        mapCurv.mask[ind] = int(bValid)
        mapMoments.mask[ind] = int(bValid)
        mapModulus.mask[ind] = int(bValid)
        mapModulusHalf.mask[ind] = int(bValid)

        if not bValid:
            continue

        # Computation

        centroid = getCenterOfSection(curImg)

        distance = []
        if (settings.mapTypesContains(EMapType.EXTERNAL_RADIUS) or
            settings.mapTypesContains(EMapType.CURVATURE)):
            distance = computeExternalRadius(contours, centroid.copy())

        moments = []
        if (settings.mapTypesContains(EMapType.MOMENT_AREA) or
            settings.mapTypesContains(EMapType.MODULUS) or
            settings.mapTypesContains(EMapType.MODULUS_HALF)):
            moments = computeSecondMoments(curImg, centroid.copy(), settings.bRight, settings.PIXEL_SIZE)

        if (settings.mapTypesContains(EMapType.EXTERNAL_RADIUS)):
            res = cartesianToPolar(curImg, contours, distance, centroid.copy(), settings.bRight)
            mapDist.map[ind] = res

        if (settings.mapTypesContains(EMapType.CORTICAL_THICK)):
            thickness = computeCorticalThikness(contours)
            res = cartesianToPolar(curImg, contours, thickness, centroid.copy(), settings.bRight)
            res *= float(settings.PIXEL_SIZE.x) * float(settings.PIXEL_SIZE.y)
            mapCort.map[ind] = res

        if (settings.mapTypesContains(EMapType.CURVATURE)):
            distanceCurv = smooth(distance, 40);
            curvature = computeCurvature(distanceCurv)
            if ind == 0:
                print(len(curvature))
                print(curvature)
            res = cartesianToPolar(curImg, contours, curvature, centroid.copy(), settings.bRight)
            if ind == 0:
                print(len(res))
                print(res)
            mapCurv.map[ind] = res

        if (settings.mapTypesContains(EMapType.MOMENT_AREA)):
            mapMoments.map[ind] = moments

        if (settings.mapTypesContains(EMapType.MODULUS) or
            settings.mapTypesContains(EMapType.MODULUS_HALF)):
            modulus, modulusHalf = computeModulus(curImg, moments, centroid.copy(), settings.PIXEL_SIZE)
            if (settings.mapTypesContains(EMapType.MODULUS)):
                mapModulus.map[ind] = modulus
            if (settings.mapTypesContains(EMapType.MODULUS_HALF)):
                mapModulusHalf.map[ind] = modulusHalf

        #print(ind)
        callback()

    return [mapDist, mapCort, mapCurv, mapMoments, mapModulus, mapModulusHalf]


def generateMapFromFile (filePath, blur :bool, flipX :bool, flipY :bool):

    mapMask = importMap(filePath)

    if flipX:
        mapMask.flip(0)

    if flipY:
        mapMask.flip(1)

    if blur:
        ksize = (3, 10)
        cv2.blur(mapMask.map, ksize)




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



class Process:

    settings: ProcessSettings = ProcessSettings()


    def retreiveSerieImages (self, dirPath :str):
        """
        Get all images (*.png) absolute paths inside a directory.
        """

        filelist = retreiveFilesInFolder(dirPath, ".png")
        filelist = np.sort(filelist)

        return filelist


    def retreiveImagesInfo (self, dirPath :str) -> bool:
        """
        Retreive the real pixel size of the sections images.
        """

        filelist = retreiveFilesInFolder(dirPath, ".info")

        if not filelist: return False

        with open(filelist[0], "r") as file:
            for line in file:
                if "pixelsize" in line:
                    splittedLine = line.split()
                    self.settings.PIXEL_SIZE.x = splittedLine[1]
                    self.settings.PIXEL_SIZE.y = splittedLine[2]

                    return True


    def rescaleImageSample (self, imageList, nbRetainImg :int = 300):
        """
        Retains a given number of images from a list of image files.
        """

        nbRetainImg = min(len(imageList), nbRetainImg)

        inc :float = float(len(imageList) + 1) / nbRetainImg
        index :float = 0

        imagesSample = []

        #dirRescaledSeriePath = self.settings.OUTPUT_DIR_PATH + "/" + self.settings.SERIE_SAMPLE_DIR_NAME

        #createFolder(dirRescaledSeriePath, True)

        for i in range(nbRetainImg):
            imgPath :str = imageList[int(index + 0.5)]
            imagesSample.append(imgPath);
            #copyFile(imgPath, dirRescaledSeriePath + "/sec_" + str(i) + ".png")
            index += inc;

        return imagesSample


    def samplePercentToSections (self, totalNbSections :int, percent :float):

        if percent == 0: return 0

        return int(percent * totalNbSections / 100)


    def computeStandFactor (self):
        factor = MathInterpreter.eval(self.settings.standFormula, self.settings.standParams)
        self.settings.standFact = factor


    def prepare (self):

        beginSample = self.samplePercentToSections(self.settings.NB_SECTIONS, self.settings.BEGIN_SAMPLE_PERCENT)
        endSample = self.samplePercentToSections(self.settings.NB_SECTIONS, self.settings.END_SAMPLE_PERCENT)
        sampleSize = self.settings.NB_SECTIONS - beginSample - endSample

        imageFiles = self.retreiveSerieImages(self.settings.SERIE_DIR_PATH)
        self.retreiveImagesInfo(self.settings.SERIE_DIR_PATH)
        imagesSampled = self.rescaleImageSample(imageFiles, sampleSize)

        reconstructedSerieFolder = self.settings.OUTPUT_DIR_PATH + "/" + self.settings.RECONSTRUCTED_SAMPLE_DIR_NAME
        createFolder(reconstructedSerieFolder, True)

        for nImg in range(len(imagesSampled)):

            curImg = reconstructImageSection(imagesSampled, nImg, self.settings)

            cv2.imwrite(reconstructedSerieFolder + "/" + "sec_" + str(nImg) + ".png", curImg)


    def updateNbSectionDone(self):
        return


    def launch (self):

        print("START")
        print(type(self.settings.NB_SECTIONS))
        beginSample = self.samplePercentToSections(self.settings.NB_SECTIONS, self.settings.BEGIN_SAMPLE_PERCENT)
        endSample = self.samplePercentToSections(self.settings.NB_SECTIONS, self.settings.END_SAMPLE_PERCENT)
        sampleSize = self.settings.NB_SECTIONS - beginSample - endSample

        print("PREPARE SAMPLE")

        imageFiles = self.retreiveSerieImages(self.settings.SERIE_DIR_PATH)
        self.retreiveImagesInfo(self.settings.SERIE_DIR_PATH)
        imagesSampled = self.rescaleImageSample(imageFiles, sampleSize)

        if (self.settings.bFlip):
            imagesSampled = imagesSampled[::-1]

        print("INIT MAPS")

        nPic :int = len(imagesSampled)

        self.mapCurv = MapMask((nPic, 360))
        self.mapDist = MapMask((nPic, 360))
        self.mapCort = MapMask((nPic, 360))
        self.mapMoments = MapMask((nPic, 360))
        self.mapMomentsJ = MapMask((nPic, 360))
        self.mapMomentsZpol = MapMask((nPic, 360))
        self.mapModulus = MapMask((nPic, 360))
        self.mapModulusHalf = MapMask((nPic, 360))

        print("LAUNCH THREADS")

        p = Pool()
        threadStep = int((nPic - endSample - beginSample) / self.settings.NB_THREAD)
        self.nbSectionsDone = 0

        result = p.starmap(launchThreadedProcess, [
            (imagesSampled, 0, 50, self.settings, self.updateNbSectionDone),
            (imagesSampled, 50, 100, self.settings, self.updateNbSectionDone),
            (imagesSampled, 100, 150, self.settings, self.updateNbSectionDone),
            (imagesSampled, 150, 200, self.settings, self.updateNbSectionDone),
            (imagesSampled, 200, 250, self.settings, self.updateNbSectionDone),
            (imagesSampled, 250, 300, self.settings, self.updateNbSectionDone)
            ])

        p.close()
        p.join()

        print("GENERATE RESULTS")

        for res in result:
            self.mapDist.merge(res[0])
            self.mapCort.merge(res[1])
            self.mapCurv.merge(res[2])
            self.mapMoments.merge(res[3])
            self.mapModulus.merge(res[4])
            self.mapModulusHalf.merge(res[5])

        if (self.settings.bStand):
            self.computeStandFactor()
            self.mapDist / self.settings.standFact
            self.mapCort / self.settings.standFact
            self.mapCurv / self.settings.standFact
            self.mapMoments / self.settings.standFact
            self.mapModulus / self.settings.standFact
            self.mapModulusHalf / self.settings.standFact

        if (self.settings.mapTypesContains(EMapType.EXTERNAL_RADIUS)):
            generateResultMap(self.mapDist, "mapExtRadius", self.settings)

        if (self.settings.mapTypesContains(EMapType.CORTICAL_THICK)):
            generateResultMap(self.mapCort, self.settings.OUTPUT_DIR_PATH + "/mapCort.txt", self.settings.bBlur)

        if (self.settings.mapTypesContains(EMapType.CURVATURE)):
            generateResultMap(self.mapCurv, self.settings.OUTPUT_DIR_PATH + "/mapCurv.txt", self.settings.bBlur)

        if (self.settings.mapTypesContains(EMapType.MOMENT_AREA)):
            generateResultMap(self.mapMoments, self.settings.OUTPUT_DIR_PATH + "/mapMoments.txt", self.settings.bBlur)

        if (self.settings.mapTypesContains(EMapType.MODULUS)):
            generateResultMap(self.mapModulus, self.settings.OUTPUT_DIR_PATH + "/mapModulus.txt", self.settings.bBlur)

        if (self.settings.mapTypesContains(EMapType.MODULUS_HALF)):
            generateResultMap(self.mapModulusHalf, self.settings.OUTPUT_DIR_PATH + "/mapModulusHalf.txt", self.settings.bBlur)




def main():

    process = Process()
    process.settings = ProcessSettings()

    process.settings.OUTPUT_DIR_PATH = "/home/patobeur/Documents/BoneMap/BoneMap/BoneMap/F87_FemR/BoneGeom"
    process.settings.SERIE_DIR_PATH = process.settings.OUTPUT_DIR_PATH + "/serie"

    #process.settings.mapTypes.append(EMapType.EXTERNAL_RADIUS)
    #process.settings.mapTypes.append(EMapType.CORTICAL_THICK)
    #process.settings.mapTypes.append(EMapType.CURVATURE)
    process.settings.mapTypes.append(EMapType.MOMENT_AREA)
    process.settings.mapTypes.append(EMapType.MODULUS)
    process.settings.mapTypes.append(EMapType.MODULUS_HALF)
    process.settings.bRight = True
    process.settings.bFlip = False

    process.launch()

    """
    section = cv2.imread("/home/patobeur/Documents/BoneMap/BoneMap/BoneMap/LV_47_FEM_R.labels040.png", cv2.IMREAD_GRAYSCALE)
    dst = process.open(section, process.settings.EROSION_SIZE, process.settings.N_ITE)

    cv2.imshow("result", dst)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
    """


if __name__ == "__main__":
    main()
