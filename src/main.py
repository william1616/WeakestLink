from tkinter import *
from tkinter import ttk
from sys import path
from os import path as osPath
#import the other gui's as moduless -> this means the guis will have to be manually initated
import server, control, gui, misc, prompt

config = misc.initConfig() #import the config and save it as a global variable
    
#overide the Tkinter toplevel class and add an extra attribute
class rootTopLevel(Toplevel):
  def __init__(self, root):
    super().__init__(root) #create the toplevel as normal by calling the super constructor
    self.root = root #add an extra attribute refering to the Toplevels parent

#setup the tkinter gui
def initTk():
  global root
  root = Tk() #create the root Tk instance and save it as a global variable
  root.title(config['Tk']['window_title']) #set the title of the root window to the value specified in the config file
  
  mainFrame = ttk.Frame(root, padding="3 3 3 3") #create a frame with 3 pixels of padding between it and the parent root instance on all 4 sides
  mainFrame.grid(column=0, row=0, sticky=(N, W, E, S)) #place the frame in the 0th row of the 0th column of its parent
  
  root.columnconfigure(0, weight=1, minsize=250) #configure the 0th column of the root instance to expand at the same rate as the root instances width, set the column to not shrink smaller than 250 pixels wide
  root.rowconfigure(0, weight=1, minsize=300) #configure the 0th row of the root instance to expand at the same rate as the root instances height, set the column to not shrink smaller than 300 pixels tall
  
  ttk.Button(mainFrame, text='Start Server', command=startServer).grid(column=0, row=0, sticky=(N, W, E, S)) #create a button to start the server gui and place it in the 0th row of the 0th column of the mainFrame
  ttk.Button(mainFrame, text='Start Control', command=startControl).grid(column=0, row=1, sticky=(N, W, E, S)) #create a button to start the server gui and place it in the 1th row of the 0th column of the mainFrame
  ttk.Button(mainFrame, text='Start GUI', command=startGUI).grid(column=0, row=2, sticky=(N, W, E, S)) #create a button to start the server gui and place it in the 2th row of the 0th column of the mainFrame
  ttk.Button(mainFrame, text='Start Prompt', command=startPrompt).grid(column=0, row=3, sticky=(N, W, E, S)) #create a button to start the server gui and place it in the 3th row of the 0th column of the mainFrame
  ttk.Button(mainFrame, text='Exit', command=root.destroy).grid(column=0, row=4, sticky=(N, W, E, S)) #create a button to start the server gui and place it in the 4th row of the 0th column of the mainFrame
  
  mainFrame.columnconfigure(0, weight=1) #setup the 0th column of the mainFrame to expand at the same rate as the width of the mainFrame
  mainFrame.rowconfigure(0, weight=1) #setup the 0th row of the mainFrame to expand at the same rate as the height of the mainFrame
  mainFrame.rowconfigure(1, weight=1) #setup the 1st row of the mainFrame to expand at the same rate as the height of the mainFrame
  mainFrame.rowconfigure(2, weight=1) #setup the 2nd row of the mainFrame to expand at the same rate as the height of the mainFrame
  mainFrame.rowconfigure(3, weight=1) #setup the 3th row of the mainFrame to expand at the same rate as the height of the mainFrame
  mainFrame.rowconfigure(4, weight=1) #setup the 4th row of the mainFrame to expand at the same rate as the height of the mainFrame
  
  root.mainloop() #Enter the programs main loop allowing tkinter callback to be handled, window updates to be processed etc
  
#start the server gui
#this functions has the same effect as the code that runns if server.__name__ == "__main__" except that the Tk() instance used to run this gui is used as the root Tk instance
def startServer():
  global root
  root.withdraw() #hide the root Tk instance (the current window)
  server.setup() #setup the server (import the config and net types declaration)
  serverWindow = rootTopLevel(root) #create a toplevel to hold the server gui
  server.initTk(serverWindow) #initialize the server tkinter gui using the Toplevel just created as the parent
  server.initListner() #initialize the server listner to listner for incomming connections
  
#start the control gui
#this functions has the same effect as the code that runns if control.__name__ == "__main__" except that the Tk() instance used to run this gui is used as the root Tk instance
def startControl():
  global root
  root.withdraw() #hide the root Tk instance (the current window)
  control.setup() #setup control (import the config and create a clientsocket)
  controlWindow = rootTopLevel(root) #create a toplevel to hold the control gui
  control.initTk(controlWindow) #initialize the control tkinter gui using the Toplevel just created as the parent
  
#start the main display gui
#this functions has the same effect as the code that runns if gui.__name__ == "__main__" except that the Tk() instance used to run this gui is used as the root Tk instance
def startGUI():
  global root
  root.withdraw() #hide the root Tk instance (the current window)
  gui.setup() #setup the main pygame gui (import the config and create a clientsocket)
  GUIWindow = rootTopLevel(root) #create a toplevel to hold the main gui
  gui.initTk(GUIWindow) #initialize the gui's tkinter gui using the Toplevel just created as the parent
  
#start the prompt gui
#this functions has the same effect as the code that runns if prompt.__name__ == "__main__" except that the Tk() instance used to run this gui is used as the root Tk instance
def startPrompt():
  global root
  root.withdraw() #hide the root Tk instance (the current window)
  prompt.setup() #setup prompt (import the config and create a clientsocket)
  promptWindow = rootTopLevel(root) #create a toplevel to hold the prompt gui
  prompt.initTk(promptWindow) #initialize the prompt tkinter gui using the Toplevel just created as the parent
  
initTk() #initatie the Tkinter GUI