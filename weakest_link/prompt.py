from tkinter import *
from tkinter import ttk, messagebox
import os.path

path = os.path.dirname(__file__)
try:
    import network, misc
except ImportError:
    import importlib.machinery
    loader = importlib.machinery.SourceFileLoader("network", os.path.join(path, "network.py"))
    network = loader.load_module("network")
    loader = importlib.machinery.SourceFileLoader("misc", os.path.join(path, "misc.py"))
    misc = loader.load_module("misc")

def variableUpdates():
    global status, question, awnser, nextQuestion, nextAwnser, contestants, message
    
    variables = network.getMessageofType('variables', [socket], False)
    #only do any processing if variables have been updated
    if variables:
        if len(variables['contestants']) == 1:
            status.set(str(list(variables['contestants'])[0]) + ' is the winner!')
        elif variables['gamemode'] == 0:
            if len(variables['contestants']) == 2:
                status.set('Final Round starting')
            else:
                status.set('Round ' + str(variables['cntRounds']) + ' starting')
        elif variables['gamemode'] == 1 or variables['gamemode'] == 4:
            if variables['gamemode'] == 1:
                status.set('Round ' + str(variables['cntRounds']) + ' Question ' + str(variables['cntRquestions']))
            else:
                status.set('Final Question ' + str(variables['cntRquestions']))
            question.set(list(variables['contestants'].keys())[variables['crtContestant']] + ': ' + variables['question'])
            nextQuestion.set(list(variables['contestants'].keys())[variables['nxtContestant']] + ': ' + variables['nxtQuestion'])
            awnser.set(variables['awnser'])
            nextAwnser.set(variables['nxtAwnser'])
            contestants.set('\n'.join([str([f, j]) for f, j in zip(variables['contestants'].keys(), variables['contestants'].values())]).replace('\'','').replace('[','').replace(']','').replace(',',':'))
        elif variables['gamemode'] == 5:
            status.set('Going to Head to Head Round')
            
    recvMessage = network.getMessageofType('pmsg', [socket], False)
    if recvMessage:
        message.set(recvMessage)
    
    try:
        #run this function again in 100ms
        if mainTopLevel.config()['class'][4] == 'Tk':
            mainTopLevel.after(100, variableUpdates)
        elif mainTopLevel.config()['class'][4] == 'Toplevel':
            mainTopLevel.root.after(100, variableUpdates)
    except TclError:
        #dont call the function again
        pass
    
def start():
    global address, socket, startFrame, waitFrame
    if network.attemptConnect(socket, address.get(), config['server']['bindPort']):
        startFrame.grid_forget()
        waitFrame.grid()
        isServerRunning()
    else:
        messagebox.showerror("Error", "Could not find server \"" + address.get() + "\"")
            
def isServerRunning():
    global mainTopLevel, socket
    
    variables = network.getMessageofType('variables', [socket], False)
    if variables and variables['gamemode'] != -1: #if no longer listing for conections
        waitFrame.grid_forget()
        mainFrame.grid()
        variableUpdates()
    else:
        #run the function every time the system is idle
        if mainTopLevel.config()['class'][4] == 'Tk':
            mainTopLevel.after(100, isServerRunning)
        elif mainTopLevel.config()['class'][4] == 'Toplevel':
            mainTopLevel.root.after(100, isServerRunning)
        
def initTk(parent):
    global address, startFrame, waitFrame, mainFrame, mainTopLevel, status, question, awnser, nextQuestion, nextAwnser, contestants, message
    
    mainTopLevel = parent
    
    startFrame = ttk.Frame(parent, padding="3 3 3 3")
    startFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    startFrame.columnconfigure(0, weight=1)
    startFrame.rowconfigure(0, weight=1)
    
    address = StringVar()
    address.set(config['server']['bindAddress'])
    
    ttk.Button(startFrame, text="Connect", command=start).grid(column=1, row=2, sticky=N)
    ttk.Button(startFrame, text="Exit", command=close).grid(column=2, row=2, sticky=N)
    ttk.Entry(startFrame, textvariable=address).grid(column=1, row=1, sticky=N)
    ttk.Label(startFrame, text="Server IP address").grid(column=2, row=1, sticky=N)
    
    mainFrame = ttk.Frame(parent, padding="3 3 3 3")
    mainFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    mainFrame.columnconfigure(0, weight=1)
    mainFrame.rowconfigure(0, weight=1)
    mainFrame.grid_remove()
    
    status = StringVar()
    question = StringVar()
    awnser = StringVar()
    nextQuestion = StringVar()
    nextAwnser = StringVar()
    contestants = StringVar()
    message = StringVar()
    
    ttk.Label(mainFrame, textvariable=status).grid(column=0, row=0, columnspan=4, sticky=N)
    ttk.Label(mainFrame, text="Question", width=133).grid(column=1, row=1, sticky=N)
    ttk.Label(mainFrame, text="Awnser", width=56).grid(column=2, row=1, sticky=N)
    ttk.Label(mainFrame, text="Current").grid(column=0, row=2, sticky=N)
    ttk.Label(mainFrame, text="Next").grid(column=0, row=3, sticky=N)
    ttk.Label(mainFrame, textvariable=question, wraplength=600, width=133).grid(column=1, row=2, sticky=N)
    ttk.Label(mainFrame, textvariable=awnser, wraplength=250, width=56).grid(column=2, row=2, sticky=N)
    ttk.Label(mainFrame, textvariable=nextQuestion, wraplength=600, width=133).grid(column=1, row=3, sticky=N)
    ttk.Label(mainFrame, textvariable=nextAwnser, wraplength=250, width=56).grid(column=2, row=3, sticky=N)
    ttk.Label(mainFrame, text="Contestants").grid(column=3, row=1, sticky=N)
    ttk.Label(mainFrame, textvariable=contestants).grid(column=3, row=2, rowspan=2, sticky=N)
    ttk.Label(mainFrame, text="Messages").grid(column=0, row=4, sticky=N)
    ttk.Label(mainFrame, textvariable=message, width=120).grid(column=1, row=4, rowspan=4, sticky=N)
    
    mainMenu = Menu(parent)
    parent['menu'] = mainMenu
    startFile = Menu(mainMenu, tearoff=0)
    startTools = Menu(mainMenu, tearoff=0)
    startHelp = Menu(mainMenu, tearoff=0)
    mainMenu.add_cascade(menu=startFile, label='File')
    mainMenu.add_cascade(menu=startTools, label='Tools')
    mainMenu.add_cascade(menu=startHelp, label='Help')
    
    startFile.add_command(label='Exit', command=close)
    
    startTools.add_command(label='What is my IP?', command=lambda: messagebox.showinfo("You IP Address is...", "\n".join(network.getIPAddress())))
    
    startHelp.add_command(label='About', command=lambda: messagebox.showinfo("About Weakest Link", "Remember to write some stuff here\nhttps://github.com/william1616/WeakestLink"))
    
    waitFrame = ttk.Frame(parent, padding="3 3 3 3")
    waitFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    waitFrame.columnconfigure(0, weight=1)
    waitFrame.rowconfigure(0, weight=1)
    
    ttk.Label(waitFrame, text="Connected to Server").grid(column=0, row=0, sticky=N)
    ttk.Label(waitFrame, text="Waiting for Server to Start").grid(column=0, row=1, sticky=N)
    
    waitFrame.grid_remove()
    
    parent.protocol("WM_DELETE_WINDOW", close)
    
def close():
    global mainTopLevel, socket
    network.closeSocket(socket)
    if mainTopLevel.config()['class'][4] == 'Toplevel': mainTopLevel.root.deiconify()
    mainTopLevel.destroy()

def setup():
    global socket, config
    socket = network.initClientSocket()
    print('Importing Config...')
    config = misc.initConfig()
    print('Config Imported')

if __name__ == '__main__':
    setup()
    root = Tk()
    root.title(config['Tk']['window_title'])
    initTk(root)
    root.mainloop()
