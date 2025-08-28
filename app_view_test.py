from libs import *
from views import *

def main():
    app = App('BoneGeom', "640x900")

    style = Style(theme='darkly')

    Grid.rowconfigure(app.root, 0, weight=1)
    Grid.columnconfigure(app.root, 0, weight=1)

    notebook = ttk.Notebook(app.root)
    notebook.grid(sticky='news', padx=10, pady=10)

    processFrame = ProcessView(notebook)
    processFrame.grid(sticky='new', padx=10, pady=10)

    generateMapFrame = GenerateMapView(notebook)
    generateMapFrame.grid(sticky='new', padx=10, pady=10)

    notebook.add(processFrame, text="Process")
    notebook.add(generateMapFrame, text="Generate Map")

    menubar = Menu(app.root)
    filemenu = Menu(menubar, tearoff=0)
    filemenu.add_command(label="Load settings", command=processFrame.loadSettings)
    filemenu.add_command(label="Save settings", command=processFrame.saveSettings)
    filemenu.add_separator()
    filemenu.add_command(label="Exit", command=app.root.quit)

    menubar.add_cascade(label="File", menu=filemenu)
    app.root.config(menu=menubar)

    app.run()


if __name__ == "__main__":
    main()
