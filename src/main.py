from tkinter import *
from tkinter import ttk
from sys import path
from os import path as osPath
import server, control, gui, misc, prompt

config = misc.initConfig()
    
class rootTopLevel(Toplevel):
    def __init__(self, root):
        Toplevel.__init__(self, root)
        self.root = root

def initTk():
    global root
    root = Tk()
    root.title(config['Tk']['window_title'])
    
    mainFrame = ttk.Frame(root, padding="3 3 3 3")
    mainFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    
    root.columnconfigure(0, weight=1, minsize=250)
    root.rowconfigure(0, weight=1, minsize=300)
    
    ttk.Button(mainFrame, text='Start Server', command=startServer).grid(column=0, row=0, sticky=(N, W, E, S))
    ttk.Button(mainFrame, text='Start Control', command=startControl).grid(column=0, row=1, sticky=(N, W, E, S))
    ttk.Button(mainFrame, text='Start GUI', command=startGUI).grid(column=0, row=2, sticky=(N, W, E, S))
    ttk.Button(mainFrame, text='Start Prompt', command=startPrompt).grid(column=0, row=3, sticky=(N, W, E, S))
    ttk.Button(mainFrame, text='Exit', command=root.destroy).grid(column=0, row=4, sticky=(N, W, E, S))
    
    mainFrame.columnconfigure(0, weight=1)
    mainFrame.rowconfigure(0, weight=1)
    mainFrame.rowconfigure(1, weight=1)
    mainFrame.rowconfigure(2, weight=1)
    mainFrame.rowconfigure(3, weight=1)
    mainFrame.rowconfigure(4, weight=1)
    
def startServer():
    global root
    root.withdraw()
    server.setup()
    serverWindow = rootTopLevel(root)
    server.initTk(serverWindow)
    server.initListner()
    
def startControl():
    global root
    root.withdraw()
    control.setup()
    controlWindow = rootTopLevel(root)
    control.initTk(controlWindow)
    
def startGUI():
    global root
    root.withdraw()
    gui.setup()
    GUIWindow = rootTopLevel(root)
    gui.initTk(GUIWindow)
    
def startPrompt():
    global root
    root.withdraw()
    prompt.setup()
    promptWindow = rootTopLevel(root)
    prompt.initTk(promptWindow)
    
initTk()
root.mainloop()
