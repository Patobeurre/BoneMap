from libs import *
from data import *
from utils import *


class GenerateMapView(Frame):

    def launchGenerateMap(self):
        mapMask = importMap(self.settings.MAP_FILE_PATH)

        generateResultMap(mapMask, self.settings.OUTPUT_DIR_PATH)


    def __init__(self, parent, **kwargs):

        super().__init__(parent, **kwargs)

        Grid.rowconfigure(self, 0, weight=1)
        Grid.rowconfigure(self, 1, weight=1)
        Grid.columnconfigure(self, 0, weight=1)

        self.settings = GenerateMapSettings()


        # File selector

        selectorFrame = Frame(self)
        selectorFrame.rowconfigure(0, weight=1)
        selectorFrame.rowconfigure(1, weight=1)
        selectorFrame.columnconfigure(0, weight=1)

        self.mapFilePath = StringVar()
        self.mapFilePath.trace_add("write", self.setMapFilePath)
        frame = Frame(selectorFrame)
        FileSelector(frame, "Select map file : ", variable=self.mapFilePath)
        frame.grid(row=0, column=0, sticky='nsew', pady=5)

        self.outputFolderPath = StringVar()
        self.outputFolderPath.trace_add("write", self.setOutputDirPath)
        frame = Frame(selectorFrame)
        DirectorySelector(frame, "Select output folder", variable=self.outputFolderPath)
        frame.grid(row=1, column=0, sticky='nsew', pady=5)

        selectorFrame.grid(row=0, column=0, sticky='new')


        # Map options

        self.bBlur = BooleanVar()
        self.bCaption = BooleanVar()
        self.bInterpolate = BooleanVar()

        mapOptionsFrame = LabelFrame(self, text='Options')

        mapOptionsFrame.grid_rowconfigure(0, weight=1)
        mapOptionsFrame.grid_rowconfigure(1, weight=1)
        mapOptionsFrame.grid_rowconfigure(2, weight=1)
        mapOptionsFrame.grid_columnconfigure(0, weight=1)

        Checkbutton(mapOptionsFrame, text="Blur", command=self.setBlur, variable=self.bBlur).grid(row=0, sticky="w", padx=5, pady=5)
        Checkbutton(mapOptionsFrame, text="Caption", command=self.setCaption, variable=self.bCaption).grid(row=1, sticky="w", padx=5, pady=5)
        Checkbutton(mapOptionsFrame, text="Interpolate cracks", command=self.setInterpolate, variable=self.bInterpolate).grid(row=2, sticky="w", padx=5, pady=5)

        mapOptionsFrame.grid(row=1, column=0, sticky='news', pady=5)


        # Standardization

        self.bStand = BooleanVar()
        self.standBodyLength = StringVar()
        self.standBodyMass = StringVar()
        self.standArticularLength = StringVar()
        self.standFormula = StringVar()

        self.standBodyLength.trace_add('write', self.setStandBodyLength)
        self.standBodyMass.trace_add('write', self.setStandBodyMass)
        self.standArticularLength.trace_add('write', self.setStandArticularLength)
        self.standFormula.trace_add('write', self.setStandFormula)

        standardizeFrame = LabelFrame(self, text='Standardize')
        standardizeFrame.grid_rowconfigure(0, weight=1)
        standardizeFrame.grid_rowconfigure(1, weight=2)
        standardizeFrame.grid_columnconfigure(0, weight=1)

        Checkbutton(standardizeFrame, text="Standardize", hoverMsg="Use standardization", command=self.setStand, variable=self.bStand, bootstyle="primary-round-toggle").grid(row=0, column=0, sticky="nw", padx=5)

        self.standParamsFrame = Frame(standardizeFrame)
        standardizeFrame.grid_rowconfigure(0, weight=2)
        standardizeFrame.grid_rowconfigure(1, weight=2)
        standardizeFrame.grid_columnconfigure(0, weight=1)
        standardizeFrame.grid_columnconfigure(1, weight=1)
        standardizeFrame.grid_columnconfigure(2, weight=1)

        frame = Frame(self.standParamsFrame)
        SpinboxLabel(frame, "Body length (L)", from_=0, to=999, textvariable=self.standBodyLength, width=5)
        frame.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        frame = Frame(self.standParamsFrame)
        SpinboxLabel(frame, "Body mass (M)", from_=0, to=999, textvariable=self.standBodyMass, width=5)
        frame.grid(row=0, column=1, sticky='w', padx=5, pady=5)
        frame = Frame(self.standParamsFrame)
        SpinboxLabel(frame, "Articular length (A)", from_=0, to=999, textvariable=self.standArticularLength, width=5)
        frame.grid(row=0, column=3, sticky='w', padx=5, pady=5)

        frame = Frame(self.standParamsFrame)
        frame.grid_columnconfigure(1, weight=3)
        Label(frame, text="Formula").grid(row=0, column=0, sticky="nw", padx=5)
        Combobox(frame, STAND_FORMULAS_PRESETS, textvariable=self.standFormula).grid(row=0, column=1, columnspan=3, sticky="new", padx=5)
        frame.grid(row=1, column=0, columnspan=3, sticky="new")

        self.standParamsFrame.grid(row=1, column=0, sticky="news", pady=5)

        standardizeFrame.grid(row=2, column=0, sticky='new', pady=10)
        self.setStand()


        # Normalization

        self.bNormMinMax = BooleanVar()
        self.bNormMMAD = BooleanVar()
        self.bNormAvg = BooleanVar()
        self.bCustomMin = BooleanVar()
        self.bCustomMax = BooleanVar()
        self.customMin = StringVar()
        self.customMax = StringVar()

        self.customMin.set(self.settings.customMin)
        self.customMax.set(self.settings.customMax)

        self.customMin.trace_add('write', self.setCustomMin)
        self.customMax.trace_add('write', self.setCustomMax)

        normalizeFrame = LabelFrame(self, text='Normalize')
        normalizeFrame.grid_rowconfigure(0, weight=1)
        normalizeFrame.grid_rowconfigure(1, weight=1)
        normalizeFrame.grid_columnconfigure(0, weight=1)
        normalizeFrame.grid_columnconfigure(1, weight=2)
        normalizeFrame.grid_columnconfigure(2, weight=2)

        minmaxFrame = Frame(normalizeFrame)
        minmaxFrame.grid_rowconfigure(0, weight=1)
        minmaxFrame.grid_rowconfigure(1, weight=2)
        minmaxFrame.grid_columnconfigure(0, weight=1)

        Checkbutton(normalizeFrame, text="MinMax", hoverMsg="Use min/max normalization", command=self.setNormMinMax, variable=self.bNormMinMax, bootstyle="primary-round-toggle").grid(row=0, column=0, sticky="nw", padx=5)

        self.customMinmaxFrame = Frame(minmaxFrame)
        self.customMinmaxFrame.grid_rowconfigure(0, weight=1)
        self.customMinmaxFrame.grid_rowconfigure(1, weight=1)
        self.customMinmaxFrame.grid_columnconfigure(0, weight=1)

        frame = Frame(self.customMinmaxFrame)
        self.spinBoxCustomMin = SpinboxLabel(frame, "Custom min : ", from_=-99999, to=99999, textvariable=self.customMin, width=5)
        frame.grid(row=0, column=1)
        frame = Frame(self.customMinmaxFrame)
        self.spinBoxCustomMax = SpinboxLabel(frame, "Custom max :", from_=-99999, to=99999, textvariable=self.customMax, width=5)
        frame.grid(row=1, column=1)
        self.customMinmaxFrame.grid(row=1, column=0, sticky='w', pady=5)

        minmaxFrame.grid(row=1, column=0, sticky='new', padx=10)

        Checkbutton(normalizeFrame, text="Average", command=self.setNormAvg, variable=self.bNormAvg, bootstyle='primary-round-toggle').grid(row=0, column=1, sticky="nw", padx=5, pady=5)
        Checkbutton(normalizeFrame, text="MMAD", command=self.setNormMMAD, variable=self.bNormMMAD, bootstyle='primary-round-toggle').grid(row=0, column=2, sticky="nw", padx=5, pady=5)

        normalizeFrame.grid(row=6, column=0, sticky='new', pady=10)
        self.setNormMinMax()


        # Launch button

        Button(self, text="Generate", command=self.launchGenerateMap).grid(row=7, column=0, sticky='se')


        self.grid(sticky='new', padx=10, pady=10)


    def enableSpinBoxRotate(self, enabled :bool):
        enableChildren(self.spinBoxRotate, enabled)

    def enableStandFrame(self, enabled :bool):
        enableChildren(self.standParamsFrame, enabled)

    def enableCustomMinMaxFrame(self, enabled :bool):
        enableChildren(self.customMinmaxFrame, enabled)


    def setMapFilePath(self, var, index, mode):
        self.settings.MAP_FILE_PATH = self.mapFilePath.get()
        print("File path: " + self.settings.MAP_FILE_PATH)
    
    def setOutputDirPath(self, var, index, mode):
        self.settings.OUTPUT_DIR_PATH = self.outputFolderPath.get()
        print("File path: " + self.settings.OUTPUT_DIR_PATH)

    def setBlur(self):
        self.settings.bBlur = bool(self.bBlur.get())

    def setCaption(self):
        self.settings.bCaption = bool(self.bCaption.get())

    def setInterpolate(self):
        self.settings.bInterpolate = bool(self.bInterpolate.get())

    def setNormMinMax(self):
        value = bool(self.bNormMinMax.get())
        self.settings.bNormMinMax = value
        self.enableCustomMinMaxFrame(value)

    def setNormMMAD(self):
        self.settings.bNormMMAD = bool(self.bNormMMAD.get())

    def setNormAvg(self):
        self.settings.bNormAvg = bool(self.bNormAvg.get())

    def setCustomMin(self, var, index, mode):
        value = float(self.customMin.get())
        self.settings.customMin = float(value)

    def setCustomMax(self, var, index, mode):
        value = float(self.customMax.get())
        self.settings.customMax = float(value)

    def setStand(self):
        self.settings.bStand = bool(self.bStand.get())
        self.enableStandFrame(self.settings.bStand)

    def setStandFormula(self, var, index, mode):
        self.settings.standFormula = self.standFormula.get()

    def setStandBodyLength(self, var, index, mode):
        value = float(self.standBodyLength.get())
        self.settings.standParams['l'] = float(value)

    def setStandBodyMass(self, var, index, mode):
        value = float(self.standBodyMass.get())
        self.settings.standParams['m'] = float(value)

    def setStandArticularLength(self, var, index, mode):
        value = float(self.standArticularLength.get())
        self.settings.standParams['a'] = float(value)

    def setFlip(self):
        self.settings.bFlip = bool(self.bFlip.get())

    def setRotate(self):
        self.settings.bRotate = bool(self.bRotate.get())
        self.updateSpinBoxRotate(self.bRotate.get())
