from mapmask import MapMask
import utils
import pandas as pd
import numpy as np
import statistics
from statsmodels import robust


FILES       = ["map_test/mapCortical_1.txt", \
               "map_test/mapCortical_2.txt", \
               "map_test/mapCortical_3.txt", \
               "map_test/mapCortical_4.txt"]

SAVE_DIR    = ""

AVERAGE     = True
DEVIATION   = True
INTERPOLATE = False
MINMAX      = True
MMAD        = True
PLOT_RESULT = True
THRESHOLD   = 2


b = 1.4826


def median_absolute_deviation(data, c=1):
    return robust.mad(data, c)


def compute_mmad(mapMask):
    mmadMapMask = MapMask(map=np.copy(mapMask.map))
    mmadMapMask.mask = mapMask.mask

    values = mapMask.getMapTrueData().flatten()

    med = np.median(values)
    mad = median_absolute_deviation(values)

    mmadMapMask.map -= med
    mmadMapMask.map /= (b * mad)

    mmadMapMask.computeMinMax()

    return mmadMapMask


def compute_mmad_group(filepaths):
    mmadMaps = []

    for filepath in filepaths:
        mapMask = utils.importMap(filepath)
        if INTERPOLATE:
            interpolate_map_dt(mapMask)
        mapMask.cleanMap()
        map = mapMask.map.flatten()
        mmadMaps.append(map)

    mmadMaps = np.array(mmadMaps)
    print(mmadMaps)

    mmadMaps = mmadMaps.T
    print(mmadMaps)

    med = []
    mad = []
    for values in mmadMaps:
        clean_values = values[values != 0]
        if clean_values.size == 0:
            clean_values = values
        med.append(np.median(clean_values))
        mad.append(median_absolute_deviation(clean_values))

    med = np.array(med)
    mad = np.array(mad)

    return med.reshape(300,360), mad.reshape(300,360)

    '''
    for idx, x in np.ndenumerate(mapMmad):
        values = []
        for mapMask in mmadMaps:
            values.append(mapMask.map(idx))
    '''


def interpolate_map_dt(mapMask, method='linear'):
    a = pd.DataFrame(mapMask.map)
    a = a.astype(float).interpolate(method=method)
    mapMask.setMap(a.to_numpy())


def meanMap(filepaths):
    ave = MapMask()

    for filepath in filepaths:
        mapMask = utils.importMap(filepath)
        if INTERPOLATE:
            interpolate_map_dt(mapMask)
        mapMask.cleanMap()
        mapMask.computeMinMax()
        utils.plot_colorMap(mapMask.map, mapMask.min, mapMask.max)

        ave.map += mapMask.map
        ave.mask += mapMask.mask

    ave.map = (ave.map.T / ave.mask).T

    ave.mask[ave.mask < THRESHOLD] = 0
    ave.mask[ave.mask >= THRESHOLD] = 1

    ave.cleanMap()
    ave.computeMinMax()

    return ave


def deviationMap(filepaths, avgMap):
    dev = MapMask()

    for filepath in filepaths:
        mapMask = utils.importMap(filepath)
        if INTERPOLATE:
            interpolate_map_dt(mapMask)
        mapMask.cleanMap()

        mapMask.map -= avgMap.map
        mapMask.map *= mapMask.map

        dev.map += mapMask.map
        dev.mask += mapMask.mask

    dev.mask[dev.mask < THRESHOLD] = 0
    dev.mask[dev.mask >= THRESHOLD] = 1

    dev.map /= avgMap.map

    dev.cleanMap()
    dev.computeMinMax()

    return dev


def main():
    ave = MapMask()
    dev = MapMask()
    med = []
    mad = []


    #if MMAD:
        #med, mad = compute_mmad_group(FILES)


    if AVERAGE or DEVIATION:
        ave = meanMap(FILES)
        utils.exportMap(ave, SAVE_DIR + "ave.txt")
        utils.plot_colorMap(ave.map, ave.min, ave.max)
        if MINMAX:
            utils.exportMap(ave.getNormMinMax(), SAVE_DIR + "ave_minmax.txt")
        if MMAD:
            mmadMap = compute_mmad(ave)
            utils.exportMap(mmadMap, SAVE_DIR + "ave_mmad.txt")
            utils.plot_colorMap(mmadMap.map, mmadMap.min, mmadMap.max)
            tanhMap = MapMask(map=np.tanh(mmadMap.map))
            tanhMap.mask = mmadMap.mask
            utils.exportMap(tanhMap, SAVE_DIR + "ave_mmad_tanh.txt")
            utils.plot_colorMap(tanhMap.map, tanhMap.min, tanhMap.max)
        '''
        if MMAD:
            mmad = np.copy(ave.map)
            mmad -= med
            mmad /= (b * mad)
            mmadMap = MapMask(mmad)
            mmadMap.mask = ave.mask
            tanhMap = MapMask(np.tanh(mmad))
            tanhMap.mask = ave.mask

            mmadMap.cleanMap()
            mmadMap.computeMinMax()
            utils.exportMap(mmadMap, SAVE_DIR + "ave_mmad.txt")
            utils.plot_colorMap(mmadMap.map, mmadMap.min, mmadMap.max)

            tanhMap.cleanMap()
            tanhMap.computeMinMax()
            utils.exportMap(tanhMap, SAVE_DIR + "ave_mmad_tanh.txt")
            utils.plot_colorMap(tanhMap.map, tanhMap.min, tanhMap.max)
        '''

        '''
        mmadMap = compute_mmad(ave)
        utils.exportMap(mmadMap, SAVE_DIR + "ave_mmad.txt")
        tanhMap = MapMask(np.tanh(mmadMap.map))
        tanhMap.mask = mmadMap.mask
        utils.exportMap(tanhMap, SAVE_DIR + "ave_mmad_tanh.txt")
        utils.plot_colorMap(tanhMap.map, tanhMap.min, tanhMap.max)
        '''

    if DEVIATION:
        dev = deviationMap(FILES, ave)
        utils.exportMap(dev, SAVE_DIR + "dev.txt")
        utils.plot_colorMap(dev.map, dev.min, dev.max)
        if MINMAX:
            utils.exportMap(dev.getNormMinMax(), SAVE_DIR + "dev_minmax.txt")
        if MMAD:
            mmadMap = compute_mmad(dev)
            utils.exportMap(mmadMap, SAVE_DIR + "dev_mmad.txt")
            tanhMap = MapMask(map=np.tanh(mmadMap.map))
            tanhMap.mask = mmadMap.mask
            utils.exportMap(tanhMap, SAVE_DIR + "dev_mmad_tanh.txt")
            utils.plot_colorMap(tanhMap.map, tanhMap.min, tanhMap.max)



'''
interpolatedMap = utils.importMap("ave.txt")
interpolate_map_dt(interpolatedMap)
utils.exportMap(interpolatedMap, "interpol.txt")
utils.plot_colorMap(interpolatedMap.map, interpolatedMap.min, interpolatedMap.max)

aveMap = meanMap(FILES)
utils.exportMap(aveMap, "ave.txt")
#print(aveMap.map)
#utils.plot_colorMap(aveMap.map, aveMap.min, aveMap.max)

mmadMap = compute_mmad(aveMap)
utils.exportMap(mmadMap, "ave_mmad.txt")
mmadMap.map = np.tanh(mmadMap.map)

utils.exportMap(mmadMap, "ave_tanh.txt")
#utils.plot_colorMap(mmadMap.map, mmadMap.min, mmadMap.max)

#utils.plot_colorMap(aveMap.map, aveMap.min, aveMap.max)

print(aveMap.getMapTrueData())
print(median_absolute_deviation(aveMap.getMapTrueData().flatten()))

normMap = aveMap.getNormMinMax()
utils.exportMap(normMap, "norm_ave.txt")

devMap = deviationMap(FILES, aveMap)
#print(devMap.map)
#utils.plot_colorMap(devMap.map, devMap.min, devMap.max)
'''

if __name__ == "__main__":
    main()
