import ast

STAND_FORMULAS_PRESETS = [
    "l",
    "a+m",
    "l/2"
]

class GenerateMapSettings:

    MASK_MAX = 255
    MASK_MIN = 0

    # Directories
    MAP_FILE_PATH :str = ""
    OUTPUT_DIR_PATH :str = ""

    # Parameters
    bFlip :bool = False
    bRotate :bool = False

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
                    setattr(self, row[0], value)
                print(getattr(self, row[0]))
        self.updateMapTypes()
