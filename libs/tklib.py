from tkinter import *
from tkinter import filedialog
import ttkbootstrap as ttk
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from tktooltip import ToolTip


class App:
    """Define the application class."""
    def __init__(self, title='App', geometry='400x200'):
        self.root = Tk()
        self.root.title(title)
        self.root.geometry(geometry)

    def run(self):
        """Run the main loop."""
        self.root.mainloop()


class Label(ttk.Label):
    """Create a Label object."""
    def __init__(self, parent, text='Label', hoverMsg="", **kwargs):
        super().__init__(parent, text=text, **kwargs)
        if hoverMsg:
            ToolTip(self, msg=hoverMsg)

class Button(ttk.Button):
    """Create a Button object."""
    def __init__(self, parent, text='Button', **kwargs):
        super().__init__(parent, text=text, **kwargs)

class Radiobutton(ttk.Radiobutton):
    """Create a RadioButton object."""
    def __init__(self, parent, text='Option 1', value='Value 1', **kwargs):
        super().__init__(parent, text=text, value=value, **kwargs)

class Checkbutton(ttk.Checkbutton):
    """Create a Checkbutton object."""
    def __init__(self, parent, text='Checkbutton', hoverMsg="", **kwargs):
        super().__init__(parent, text=text, **kwargs)
        if hoverMsg:
            ToolTip(self, msg=hoverMsg)

class Entry(ttk.Entry):
    """Create a Entry object."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

class Frame(ttk.Frame):
    """Create a Frame object."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

class LabelFrame(ttk.LabelFrame):
    """Create a LabelFrame object."""
    def __init__(self, parent, text='', **kwargs):
        super().__init__(parent, text=text, **kwargs)

class Spinbox(ttk.Spinbox):
    """Create a Spinbox object."""
    def __init__(self, parent, **kwargs):
        super().__init__(parent, **kwargs)

class OptionMenu(ttk.OptionMenu):
    """Create an OptionMenu object."""
    def __init__(self, parent, variable, *values, **kwargs):
        super().__init__(parent, variable, *values, **kwargs)

class Combobox(ttk.Combobox):
    """Create a Combobox object."""
    def __init__(self, parent, values=[], **kwargs):
        super().__init__(parent, **kwargs)
        self["values"] = values

class Progressbar(ttk.Progressbar):
    """Create a Progressbar object."""
    def __init__(self, parent, value=0, **kwargs):
        super().__init__(parent, **kwargs)
        self['value'] = value

    def progress(self, value):
        self['value'] += value


class ProgressbarWithValue:

    def __init__(self, parent, value=0, maximum=100, **kwargs):
        Grid.columnconfigure(parent, 0, weight=2)
        self.progressbar = Progressbar(parent, value=value, maximum=maximum)
        self.label = Label(parent, text=str(value) + '%')
        self.progressbar.grid(row=0, column=0, sticky='news')
        self.label.grid(row=0, column=1, sticky='nsw')

    def update(self, value):
        self.progressbar.progress(value)
        self.label.config(text=str(value) + '%')



class SpinboxLabel:

    def __init__(self, parent, labelTxt :str, hoverMsg="", **kwargs):
        Grid.columnconfigure(parent,0,weight=2)
        Label(parent, text=labelTxt, hoverMsg=hoverMsg).grid(row=0, column=0)
        self.spinBox = Spinbox(parent, **kwargs)
        self.spinBox.grid(row=0, column=1, sticky='nswe')


class DirectorySelector:

    def selectFolder(self):
        self.path = filedialog.askdirectory()
        self.entry.delete(0, END)
        self.entry.insert(0, self.path)

    def __init__(self, parent, labelTxt :str, variable, inputFieldPlaceholder :str = ''):
        self.path = variable
        Grid.rowconfigure(parent,0,weight=1)
        Grid.columnconfigure(parent,1,weight=2)
        Label(parent, text=labelTxt).grid(row=0, column=0, sticky='w')
        self.entry = Entry(parent, textvariable=self.path)
        self.entry.grid(row=0, column=1, sticky='nsew')
        button = Button(parent, text="...", width=3, command=self.selectFolder, bootstyle='secondary').grid(row=0, column=11, sticky='e')


class FileSelector:

    def selectFile(self):
        self.path = filedialog.askopenfilename()
        self.entry.delete(0, END)
        self.entry.insert(0, self.path)

    def __init__(self, parent, labelTxt :str, variable, inputFieldPlaceholder :str = ''):
        self.path = variable
        Grid.rowconfigure(parent,0,weight=1)
        Grid.columnconfigure(parent,1,weight=2)
        Label(parent, text=labelTxt).grid(row=0, column=0, sticky='w')
        self.entry = Entry(parent, textvariable=self.path)
        self.entry.grid(row=0, column=1, sticky='nsew')
        button = Button(parent, text="...", width=3, command=self.selectFile, bootstyle='secondary').grid(row=0, column=11, sticky='e')



def enableChildren(parent, enabled):
    for child in parent.winfo_children():
        wtype = child.winfo_class()
        if wtype in ('Label', 'TLabel'):
            child.configure(bootstyle="active" if enabled else "secondary")
        elif wtype not in ('Frame','Labelframe','TFrame','TLabelframe'):
            newState = NORMAL if enabled else DISABLED
            child.configure(state=newState)
        else:
            enableChildren(child, enabled)
