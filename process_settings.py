from utils import Point
from enum import Enum
import ast


class EMapType(Enum):
    CORTICAL_THICK = 1
    CURVATURE = 2
    MODULUS = 3
    MODULUS_HALF = 4
    EXTERNAL_RADIUS = 5
    MOMENT_AREA = 6

STAND_FORMULAS_PRESETS = [
    "l",
    "a+m",
    "l/2"
]



class ProcessSettings:
    '''
    All variables used for an analysis
    '''

    MASK_MAX = 255
    MASK_MIN = 0

    # Directories
    MAIN_DIR_PATH :str = ""
    OUTPUT_DIR_PATH :str = ""
    SERIE_DIR_PATH :str = ""
    SERIE_DIR_NAME :str = "serie"
    SERIE_SAMPLE_DIR_NAME :str = "rescaledSerie"
    RECONSTRUCTED_SAMPLE_DIR_NAME :str = "reconstructedSerie"

    # Real size of a pixel
    PIXEL_SIZE :Point = Point(1,1)

    # Sections
    NB_SECTIONS :int = 300
    BEGIN_SAMPLE_PERCENT :float = 0
    END_SAMPLE_PERCENT :float = 0
    NB_THREAD :int = 4

    # Image operations
    N_ITE :int = 5
    EROSION_SIZE :int = 1

    nbIterMorpho :int = 5

    # Parameters
    bFlip :bool = False
    bRight :bool = False
    bRotate :bool = False
    bSkipPrepare :bool = False

    sectionRotAngle :float = 0

    bMoments :bool = False
    bModulus :bool = False
    bModulusHalf :bool = False
    bCurv :bool = False
    bDistance :bool = False
    bCortical :bool = False

    mapTypes = []

    bInfoSection :bool = False

    # Map options
    bBlur :bool = False
    bCaption :bool = False
    bInterpolate :bool = False

    # Standardization

    bStand :bool = False
    standParams = {
        "a" : 0,
        "l" : 0,
        "m" : 0
    }
    standFormula :str = ""
    standFact :float = 1

    # Normalization

    bNormMinMax :bool = False
    bNormAvg :bool = False
    bNormMMAD :bool = False
    customMin :float = 0
    customMax :float = 1


    def mapTypesContains(self, type :EMapType):

        return type in self.mapTypes


    def updateMapTypes(self):

        self.mapTypes = []
        if (self.bDistance): self.mapTypes.append(EMapType.EXTERNAL_RADIUS)
        if (self.bCortical): self.mapTypes.append(EMapType.CORTICAL_THICK)
        if (self.bCurv): self.mapTypes.append(EMapType.CURVATURE)
        if (self.bMoments): self.mapTypes.append(EMapType.MOMENT_AREA)
        if (self.bModulus): self.mapTypes.append(EMapType.MODULUS)
        if (self.bModulusHalf): self.mapTypes.append(EMapType.MODULUS_HALF)


    def export(self, filePath :str):
        with open(filePath, 'w') as f:
            f.write('\n'.join(["%s=%s" % (a, getattr(self, a)) for a in dir(self) if not a.startswith("__") and not callable(getattr(self, a))]))

    def importFromFile(self, filePath :str):
        with open(filePath, 'r') as f:
            for line in f:
                row = line.strip().split('=')
                if not len(row) == 2: continue
                value = row[1]
                try:
                    castedValue = ast.literal_eval(value)
                    setattr(self, row[0], castedValue)
                except Exception as e:
                    print(e)
                    if value.startswith("Point"):
                        setattr(self, row[0], Point.parse(value))
                    else:
                        setattr(self, row[0], value)
                print(getattr(self, row[0]))
        self.updateMapTypes()
