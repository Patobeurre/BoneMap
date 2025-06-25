from libs import *
from views import *

def main():
    app = App('BoneGeom', "640x900")

    style = Style(theme='darkly')

    Grid.rowconfigure(app.root, 0, weight=1)
    Grid.columnconfigure(app.root, 0, weight=1)

    mainFrame = GenerateMapView(app.root)
    mainFrame.grid(sticky='new', padx=10, pady=10)

    app.run()


if __name__ == "__main__":
    main()
