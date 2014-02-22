from tkinter import *
from tkinter import ttk
import threading, time, network, math, misc

socket = network.initClientSocket()
variables = {'gamemode': -1}

class listner(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.end = False
    def run(self):
        global variables, socket
        while not self.end:
            variables = network.getMessageofType('variables', [socket])
    def join(self):
        self.end = True
        time.sleep(0.1)
        threading.Thread.join(self)
        
receive = listner()

def start():
    global address, socket, startFrame, waitFrame
    if network.attemptConnect(socket, address.get(), config['server']['bindPort']):
        startFrame.grid_forget()
        waitFrame.grid()
        isServerRunning()

def isServerRunning():
    global socket, startTopLevel, mainTopLevel, variables, receive
    
    variables = network.getMessageofType('variables', [socket], False)
    if variables and variables['gamemode'] != -1: #if no longer listning for conections
        receive.start()
        variableUpdates()
        startTopLevel.withdraw()
        mainTopLevel.deiconify()
    else:
        #run the function every time the system is idle
        if mainTopLevel.config()['class'][4] == 'Tk':
            mainTopLevel.after_idle(isServerRunning)
        elif mainTopLevel.config()['class'][4] == 'Toplevel':
            mainTopLevel.root.after_idle(isServerRunning)

def removeContestant(contestantIndex):
    global voteFrame, mainFrame, socket
    voteTopLevel.withdraw()
    mainTopLevel.deiconify()
    network.sendMessage('cmd', contestantIndex, socket)

def initTk(parent):
    global address, question, status, cur_money, bank, voteVar, voteButton, config, startFrame, startTopLevel, mainTopLevel, voteTopLevel, waitFrame

    mainTopLevel = parent
    parent.title(config['Tk']['window_title'])
    parent.resizable(False, False)
    parent.withdraw()
    
    startTopLevel = Toplevel(parent)
    startTopLevel.title(config['Tk']['window_title'])
    startTopLevel.resizable(False, False)
    
    startFrame = ttk.Frame(startTopLevel, padding="3 3 3 3")
    startFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    startFrame.columnconfigure(0, weight=1)
    startFrame.rowconfigure(0, weight=1)

    address = StringVar()
    address.set('localhost')

    ttk.Button(startFrame, text="Connect", command=start).grid(column=1, row=2, sticky=N)
    ttk.Button(startFrame, text="Exit", command=close).grid(column=2, row=2, sticky=N)
    ttk.Entry(startFrame, textvariable=address).grid(column=1, row=1, sticky=N)
    ttk.Label(startFrame, text="Server IP address").grid(column=2, row=1, sticky=N)

    mainFrame = ttk.Frame(parent, padding="3 3 3 3")
    mainFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    mainFrame.columnconfigure(0, weight=1)
    mainFrame.rowconfigure(0, weight=1)

    question = StringVar()
    status = StringVar()
    cur_money = IntVar()
    bank = IntVar()

    ttk.Label(mainFrame, textvariable=status, width=100, background='red').grid(column=1, row=1, sticky=N)
    ttk.Label(mainFrame, textvariable=question, width=100).grid(column=1, row=2, sticky=N)
    ttk.Label(mainFrame, text='Money: ').grid(column=4, row=1, sticky=N)
    ttk.Label(mainFrame, text='Bank: ').grid(column=4, row=2, sticky=N)
    ttk.Label(mainFrame, textvariable=cur_money).grid(column=5, row=1, sticky=N)
    ttk.Label(mainFrame, textvariable=bank).grid(column=5, row=2, sticky=N)
    ttk.Button(mainFrame, text="Correct", command=lambda: network.sendMessage('cmd', 1, socket)).grid(column=2, row=1, sticky=N)
    ttk.Button(mainFrame, text="Incorrect", command=lambda: network.sendMessage('cmd', 2, socket)).grid(column=2, row=2, sticky=N)
    ttk.Button(mainFrame, text="Bank", command=lambda: network.sendMessage('cmd', 3, socket)).grid(column=3, row=2, sticky=N)
    ttk.Button(mainFrame, text="Time Up", command=lambda: network.sendMessage('cmd', 4, socket)).grid(column=3, row=1, sticky=N)
    
    voteTopLevel = Toplevel(parent)
    voteTopLevel.title(config['Tk']['window_title'])
    voteTopLevel.resizable(False, False)
    voteTopLevel.withdraw()
    
    voteFrame = ttk.Frame(voteTopLevel, padding="3 3 3 3")
    voteFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    voteFrame.columnconfigure(0, weight=1)
    voteFrame.rowconfigure(0, weight=1)
    
    voteVar = []
    voteButton = []
    
    waitFrame = ttk.Frame(startTopLevel, padding="3 3 3 3")
    waitFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    waitFrame.columnconfigure(0, weight=1)
    waitFrame.rowconfigure(0, weight=1)
    
    ttk.Label(waitFrame, text="Connected to Server").grid(column=0, row=0, sticky=N)
    ttk.Label(waitFrame, text="Waiting for Server to Start").grid(column=0, row=1, sticky=N)
    
    waitFrame.grid_remove()
    
    for i in range(0, 8):
        voteVar.append(StringVar())
        voteButton.append(ttk.Button(voteFrame, textvariable=voteVar[i], command=lambda index=i: removeContestant(index)))
        voteButton[i].grid(column=i % 4, row=math.ceil((1 + i) / 4), sticky=N)
        
    mainTopLevel.protocol("WM_DELETE_WINDOW", close)
    startTopLevel.protocol("WM_DELETE_WINDOW", close)
    voteTopLevel.protocol("WM_DELETE_WINDOW", close)

def close():
    global receive
    if receive.isAlive(): receive.join()
    if mainTopLevel.config()['class'][4] == 'Toplevel': mainTopLevel.root.deiconify()
    mainTopLevel.destroy()
    startTopLevel.destroy()
    voteTopLevel.destroy()
        
def variableUpdates():
    global question, status, cur_money, bank, startTopLevel, mainTopLevel, voteTopLevel
    if variables['gamemode'] == 0:
        voteTopLevel.withdraw()
        status.set('Round ' + str(variables['cntRounds']) + ' starting')
        mainTopLevel.deiconify()
    elif variables['gamemode'] == 1:
        voteTopLevel.withdraw()
        status.set('Round ' + str(variables['cntRounds']) + ' Question ' + str(variables['cntRquestions']))
        question.set(list(variables['contestants'].keys())[variables['crtContestant']] + ': ' + variables['question'])
        cur_money.set(list(variables['money'])[variables['correct']])
        bank.set(variables['bank'])
        mainTopLevel.deiconify()
    elif variables['gamemode'] == 2:
        mainTopLevel.withdraw()
        contestantList = list(variables['contestants'].keys())
        for i in range(0, 8):
            try:
                voteVar[i].set(contestantList[i])
            except IndexError:
                voteButton[i].grid_forget()
        voteTopLevel.deiconify()
    variables['gamemode'] = -1 #this only effects the local var not the var on the server
    
    #run this function again in 100ms
    if mainTopLevel.config()['class'][4] == 'Tk':
        mainTopLevel.after(100, variableUpdates)
    elif mainTopLevel.config()['class'][4] == 'Toplevel':
        mainTopLevel.root.after(100, variableUpdates)
        
def setup():
    global config
    print('Importing Config...')
    config = misc.initConfig()
    print('Config Imported')

if __name__ == '__main__':
    setup()
    root = Tk()
    initTk(root)
    root.mainloop()
