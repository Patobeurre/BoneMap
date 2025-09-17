from libs import *
from data import *
from core import *


class MainWindow:

    def loadSettings(self):
        file = filedialog.askopenfilename(defaultextension=".txt")
        self.process_settings.importFromFile(file)
        print(type(self.process_settings.NB_SECTIONS))
        self.updateUI()

    def saveSettings(self):
        file = filedialog.asksaveasfilename(defaultextension=".txt")
        self.process_settings.export(file)

    def isValidSettings(self) -> bool:
        return True

    def prepareProcess(self):
        self.process.settings = self.process_settings
        if self.isValidSettings:
            self.process.prepare()


    def updateProgressBar(self):
        return
        #self.progressBar.update(1)

    def launchProcess(self):
        self.process_settings.updateMapTypes()
        #self.process.settings = self.process_settings
        if self.isValidSettings:
            try:
                self.process.launch()
            except Exception as e:
                #TODO
                print(str(e))


    def __init__(self):

        self.process = Process()
        self.process_settings = ProcessSettings()
        self.process.settings = self.process_settings

        app = App('BoneGeom', "640x900")

        style = Style(theme='darkly')

        menubar = Menu(app.root)
        filemenu = Menu(menubar, tearoff=0)
        filemenu.add_command(label="Load settings", command=self.loadSettings)
        filemenu.add_command(label="Save settings", command=self.saveSettings)
        filemenu.add_separator()
        filemenu.add_command(label="Exit", command=app.root.quit)

        menubar.add_cascade(label="File", menu=filemenu)
        app.root.config(menu=menubar)

        Grid.rowconfigure(app.root,0,weight=1)
        Grid.columnconfigure(app.root,0,weight=1)

        mainFrame = Frame(app.root)
        mainFrame.rowconfigure(0, weight=1)
        mainFrame.rowconfigure(1, weight=1)
        mainFrame.rowconfigure(2, weight=1)
        mainFrame.rowconfigure(3, weight=1)
        mainFrame.rowconfigure(4, weight=1)
        mainFrame.rowconfigure(5, weight=2)
        mainFrame.columnconfigure(0, weight=1)


        # Folder selectors

        foldersFrame = Frame(mainFrame)
        foldersFrame.rowconfigure(0, weight=1)
        foldersFrame.rowconfigure(1, weight=1)
        foldersFrame.columnconfigure(0, weight=1)

        self.serieFolderPath = StringVar()
        self.serieFolderPath.trace_add("write", self.setSerieFolder)
        frame = Frame(foldersFrame)
        DirectorySelector(frame, "Select serie folder", variable=self.serieFolderPath)
        frame.grid(row=0, column=0, sticky='nsew', pady=5)

        self.outputFolderPath = StringVar()
        self.outputFolderPath.trace_add("write", self.setOutputFolder)
        frame = Frame(foldersFrame)
        DirectorySelector(frame, "Select output folder", variable=self.outputFolderPath)
        frame.grid(row=1, column=0, sticky='nsew', pady=5)

        foldersFrame.grid(row=0, column=0, sticky='new')

        # Prepare Serie

        self.bSkipPrepare = BooleanVar()
        Checkbutton(mainFrame, text="Skip preparation", hoverMsg="Skip the reconstruction process", command=self.setSkipPrepare, variable=self.bSkipPrepare).grid(row=1, column=0, sticky='w')


        self.nbSections = StringVar()
        self.nbSections.set(self.process_settings.NB_SECTIONS)
        self.beginSample = StringVar()
        self.endSample = StringVar()
        self.nbSections.trace_add('write', self.setNbSections)
        self.beginSample.trace_add('write', self.setBeginSample)
        self.endSample.trace_add('write', self.setEndSample)

        self.prepareFrame = LabelFrame(mainFrame, text='Prepare serie')
        self.prepareFrame.rowconfigure(0, weight=1)
        self.prepareFrame.columnconfigure(2, weight=2)

        frame = Frame(self.prepareFrame)
        SpinboxLabel(frame, "Number of sections", from_=0, to=999, width=5)
        frame.grid(row=0, column=0, sticky='w', padx=5, pady=5)
        frame = Frame(self.prepareFrame)
        SpinboxLabel(frame, "begin sample (%)", hoverMsg="Percentage of upper missing sections", from_=0, to=100, width=5)
        frame.grid(row=1, column=0, sticky='w', padx=5, pady=5)
        frame = Frame(self.prepareFrame)
        SpinboxLabel(frame, "end sample (%)", hoverMsg="Percentage of lower missing sections", from_=0, to=100, width=5)
        frame.grid(row=1, column=1, sticky='w', padx=5, pady=5)
        frame = Frame(self.prepareFrame)
        Button(frame, text="Prepare Serie").grid()
        frame.grid(row=2, column=2, sticky='e', padx=5, pady=5)

        self.prepareFrame.grid(row=2, column=0, sticky='nwe', pady=10)


        # Sections params

        sectionParamFrame = Frame(mainFrame)
        sectionParamFrame.rowconfigure(0, weight=1)
        sectionParamFrame.rowconfigure(1, weight=1)
        sectionParamFrame.columnconfigure(0, weight=1)
        sectionParamFrame.columnconfigure(1, weight=1)

        self.bFlip = BooleanVar()
        self.bRight = BooleanVar()
        self.bRight.trace_add('write', self.setRight)

        Radiobutton(sectionParamFrame, text="Left", value=False, variable=self.bRight).grid(row=0, column=0, sticky='w')
        Radiobutton(sectionParamFrame, text="Right", value=True, variable=self.bRight).grid(row=0, column=1, sticky='w')

        #Checkbutton(sectionParamFrame, text="is Right", hoverMsg="Is right bone", command=self.setRight, variable=self.bRight).grid(row=1, column=1, sticky='w')
        Checkbutton(sectionParamFrame, text="Flip", hoverMsg="Flip bone upside down", command=self.setFlip, variable=self.bFlip, bootstyle="primary-round-toggle").grid(row=1, column=0, sticky='w')


        self.bRotate = BooleanVar()
        self.sectionRotAngle = StringVar()
        self.sectionRotAngle.trace_add('write', self.setRotationAngle)

        frame = Frame(sectionParamFrame)
        Checkbutton(frame, text="Rotate :", hoverMsg="Apply clockwise rotation to sections", command=self.setRotate, variable=self.bRotate, bootstyle="primary-round-toggle").grid(row=0, column=0)
        self.spinBoxRotate = Spinbox(frame, from_=0, to=359, textvariable=self.sectionRotAngle, width=5)
        self.enableSpinBoxRotate(self.bRotate.get())
        self.spinBoxRotate.grid(row=0, column=1)
        frame.grid(row=1, column=1, sticky='w')

        sectionParamFrame.grid(row=3, column=0, sticky='new', pady=10)


        mapFrame = Frame(mainFrame)
        mapFrame.grid_rowconfigure(0, weight=1)
        mapFrame.grid_columnconfigure(0, weight=1)
        mapFrame.grid_columnconfigure(1, weight=2)

        # Map types

        self.bDistance = BooleanVar()
        self.bCortical = BooleanVar()
        self.bCurv = BooleanVar()
        self.bMoments = BooleanVar()
        self.bModulus = BooleanVar()
        self.bModulusHalf = BooleanVar()

        operationFrame = LabelFrame(mapFrame, text='Map types')

        operationFrame.grid_rowconfigure(0, weight=1)
        operationFrame.grid_rowconfigure(1, weight=1)
        operationFrame.grid_rowconfigure(2, weight=1)
        operationFrame.grid_rowconfigure(3, weight=1)
        operationFrame.grid_rowconfigure(4, weight=1)
        operationFrame.grid_rowconfigure(5, weight=1)
        operationFrame.grid_columnconfigure(0, weight=1)

        Checkbutton(operationFrame, text="External radius", command=self.setOperations, variable=self.bDistance).grid(row=0, sticky="w", padx=5, pady=5)
        Checkbutton(operationFrame, text="Cortical thickness", command=self.setOperations, variable=self.bCortical).grid(row=1, sticky="w", padx=5, pady=5)
        Checkbutton(operationFrame, text="Curvature", command=self.setOperations, variable=self.bCurv).grid(row=2, sticky="w", padx=5, pady=5)
        Checkbutton(operationFrame, text="Second Moments", command=self.setOperations, variable=self.bMoments).grid(row=3, sticky="w", padx=5, pady=5)
        Checkbutton(operationFrame, text="Modulus", command=self.setOperations, variable=self.bModulus).grid(row=4, sticky="w", padx=5, pady=5)
        Checkbutton(operationFrame, text="Modulus (half section)", command=self.setOperations, variable=self.bModulusHalf).grid(row=5, sticky="w", padx=5, pady=5)

        operationFrame.grid(row=4, column=0, sticky='news')


        # Map options

        self.bBlur = BooleanVar()
        self.bCaption = BooleanVar()
        self.bInterpolate = BooleanVar()
        self.bInfoSection = BooleanVar()

        mapOptionsFrame = LabelFrame(mapFrame, text='Options')

        mapOptionsFrame.grid_rowconfigure(0, weight=1)
        mapOptionsFrame.grid_rowconfigure(1, weight=1)
        mapOptionsFrame.grid_rowconfigure(2, weight=1)
        operationFrame.grid_columnconfigure(0, weight=1)

        Checkbutton(mapOptionsFrame, text="Generate sections info", command=self.setInfoSection, variable=self.bInfoSection).grid(row=0, sticky="w", padx=5, pady=5)
        Checkbutton(mapOptionsFrame, text="Blur", command=self.setBlur, variable=self.bBlur).grid(row=1, sticky="w", padx=5, pady=5)
        Checkbutton(mapOptionsFrame, text="Caption", command=self.setCaption, variable=self.bCaption).grid(row=2, sticky="w", padx=5, pady=5)
        Checkbutton(mapOptionsFrame, text="Interpolate cracks", command=self.setInterpolate, variable=self.bInterpolate).grid(row=3, sticky="w", padx=5, pady=5)

        mapOptionsFrame.grid(row=4, column=1, sticky='news', padx=(5,0))

        mapFrame.grid(row=4, column=0, sticky='new', pady=10)


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

        standardizeFrame = LabelFrame(mainFrame, text='Standardize')
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

        standardizeFrame.grid(row=5, column=0, sticky='new', pady=10)
        self.setStand()


        # Normalization

        self.bNormMinMax = BooleanVar()
        self.bNormMMAD = BooleanVar()
        self.bNormAvg = BooleanVar()
        self.bCustomMin = BooleanVar()
        self.bCustomMax = BooleanVar()
        self.customMin = StringVar()
        self.customMax = StringVar()

        self.customMin.set(self.process_settings.customMin)
        self.customMax.set(self.process_settings.customMax)

        self.customMin.trace_add('write', self.setCustomMin)
        self.customMax.trace_add('write', self.setCustomMax)

        normalizeFrame = LabelFrame(mainFrame, text='Normalize')
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

        progressBarFrame = Frame(mainFrame)
        self.progressBar = ProgressbarWithValue(progressBarFrame, value=0, maximum=100, orient="horizontal", length=200, mode="determinate", takefocus=True)
        progressBarFrame.grid(row=7, column=0, sticky='news', padx=(0,10))

        Button(mainFrame, text="Launch", command=self.launchProcess).grid(row=7, column=1, sticky='se')


        mainFrame.grid(sticky='new', padx=10, pady=10)

        app.run()


    def updateUI(self):
        self.serieFolderPath.set(self.process_settings.SERIE_DIR_PATH)
        self.outputFolderPath.set(self.process_settings.OUTPUT_DIR_PATH)

        self.bSkipPrepare.set(self.process_settings.bSkipPrepare)
        self.enablePrepareFrame(not self.process_settings.bSkipPrepare)

        self.nbSections.set(self.process_settings.NB_SECTIONS)
        self.beginSample.set(self.process_settings.BEGIN_SAMPLE_PERCENT)
        self.endSample.set(self.process_settings.END_SAMPLE_PERCENT)

        self.bFlip.set(self.process_settings.bFlip)
        self.bRight.set(self.process_settings.bRight)
        self.bRotate.set(self.process_settings.bRotate)
        self.sectionRotAngle.set(self.process_settings.sectionRotAngle)
        self.enableSpinBoxRotate(self.process_settings.bRotate)

        self.bDistance.set(self.process_settings.bDistance)
        self.bCortical.set(self.process_settings.bCortical)
        self.bCurv.set(self.process_settings.bCurv)
        self.bMoments.set(self.process_settings.bMoments)
        self.bModulus.set(self.process_settings.bModulus)
        self.bModulusHalf.set(self.process_settings.bModulusHalf)

        self.bBlur.set(self.process_settings.bBlur)
        self.bCaption.set(self.process_settings.bCaption)
        self.bInterpolate.set(self.process_settings.bInterpolate)
        self.bInfoSection.set(self.process_settings.bInfoSection)

        self.bStand.set(self.process_settings.bStand)
        self.standBodyLength.set(self.process_settings.standParams['l'])
        self.standBodyMass.set(self.process_settings.standParams['m'])
        self.standArticularLength.set(self.process_settings.standParams['a'])
        self.standFormula.set(self.process_settings.standFormula)
        self.enableStandFrame(self.process_settings.bStand)

        self.bNormMinMax.set(self.process_settings.bNormMinMax)
        self.bNormMMAD.set(self.process_settings.bNormMMAD)
        self.bNormAvg.set(self.process_settings.bNormAvg)
        self.customMin.set(self.process_settings.customMin)
        self.customMax.set(self.process_settings.customMax)
        enableChildren(self.customMinmaxFrame, self.process_settings.bNormMinMax)


    def enableSpinBoxRotate(self, enabled :bool):
        enableChildren(self.spinBoxRotate, enabled)

    def enablePrepareFrame(self, enabled :bool):
        enableChildren(self.prepareFrame, enabled)

    def enableStandFrame(self, enabled :bool):
        enableChildren(self.standParamsFrame, enabled)

    def enableCustomMinMaxFrame(self, enabled :bool):
        enableChildren(self.customMinmaxFrame, enabled)


    # Setters

    def setSerieFolder(self, var, index, mode):
        self.process_settings.SERIE_DIR_PATH = self.serieFolderPath.get()
        print("Serie folder path: " + self.process_settings.SERIE_DIR_PATH)

    def setOutputFolder(self, var, index, mode):
        self.process_settings.OUTPUT_DIR_PATH = self.outputFolderPath.get()
        print("Output folder path: " + self.process_settings.OUTPUT_DIR_PATH)

    def setOperations(self):
        self.process_settings.bDistance = bool(self.bDistance.get())
        self.process_settings.bCortical = bool(self.bCortical.get())
        self.process_settings.bCurv = bool(self.bCurv.get())
        self.process_settings.bMoments = bool(self.bMoments.get())
        self.process_settings.bModulus = bool(self.bModulus.get())
        self.process_settings.bModulusHalf = bool(self.bModulusHalf.get())

    def setFlip(self):
        self.process_settings.bFlip = bool(self.bFlip.get())

    def setRight(self, var, index, mode):
        self.process_settings.bRight = bool(self.bRight.get())

    def setRotate(self):
        self.process_settings.bRotate = bool(self.bRotate.get())
        self.updateSpinBoxRotate(self.bRotate.get())

    def setRotationAngle(self, var, index, mode):
        value = float(self.sectionRotAngle.get())
        if value:
            if float(value) > 359:
                self.sectionRotAngle.set(359)
            if float(value) < -359:
                self.sectionRotAngle.set(-359)
            self.process_settings.sectionRotAngle = float(value)

    def setNbSections(self, var, index, mode):
        self.process_settings.NB_SECTIONS = int(self.nbSections.get())

    def setBeginSample(self, var, index, mode):
        self.process_settings.BEGIN_SAMPLE_PERCENT = int(self.beginSample.get())

    def setEndSample(self, var, index, mode):
        self.process_settings.END_SAMPLE_PERCENT = int(self.endSample.get())

    def setSkipPrepare(self):
        self.process_settings.bSkipPrepare = bool(self.bSkipPrepare.get())
        self.enablePrepareFrame(not self.process_settings.bSkipPrepare)

    def setBlur(self):
        self.process_settings.bBlur = bool(self.bBlur.get())

    def setCaption(self):
        self.process_settings.bCaption = bool(self.bCaption.get())

    def setInterpolate(self):
        self.process_settings.bInterpolate = bool(self.bInterpolate.get())

    def setInfoSection(self):
        self.process_settings.bInfoSection = bool(self.bInfoSection.get())

    def setNormMinMax(self):
        value = bool(self.bNormMinMax.get())
        self.process_settings.bNormMinMax = value
        self.enableCustomMinMaxFrame(value)

    def setNormMMAD(self):
        self.process_settings.bNormMMAD = bool(self.bNormMMAD.get())

    def setNormAvg(self):
        self.process_settings.bNormAvg = bool(self.bNormAvg.get())

    def setCustomMin(self, var, index, mode):
        value = float(self.customMin.get())
        self.process_settings.customMin = float(value)

    def setCustomMax(self, var, index, mode):
        value = float(self.customMax.get())
        self.process_settings.customMax = float(value)

    def setStand(self):
        self.process_settings.bStand = bool(self.bStand.get())
        self.enableStandFrame(self.process_settings.bStand)

    def setStandFormula(self, var, index, mode):
        self.process_settings.standFormula = self.standFormula.get()

    def setStandBodyLength(self, var, index, mode):
        value = float(self.standBodyLength.get())
        self.process_settings.standParams['l'] = float(value)

    def setStandBodyMass(self, var, index, mode):
        value = float(self.standBodyMass.get())
        self.process_settings.standParams['m'] = float(value)

    def setStandArticularLength(self, var, index, mode):
        value = float(self.standArticularLength.get())
        self.process_settings.standParams['a'] = float(value)
