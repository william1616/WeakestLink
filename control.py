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
        while True:
            variables = network.getMessageofType('variables', [socket])
            if self.end == True:
                break
    def join(self):
            self.end = True

def start():
    global address, socket, startTopLevel, mainTopLevel, variables
    if network.attemptConnect(socket, address.get(), config['server']['bindPort']):
        receive = listner()
        receive.start()
        variableUpdates()
        startTopLevel.withdraw()
        mainTopLevel.deiconify()

def removeContestant(contestantIndex):
    global voteFrame, mainFrame, socket
    voteTopLevel.withdraw()
    mainTopLevel.deiconify()
    network.sendMessage('cmd', contestantIndex, socket)

def initTk(parent):
    global address, question, status, cur_money, bank, voteVar, voteButton, config, startTopLevel, mainTopLevel, voteTopLevel

    mainTopLevel = parent
    parent.title(config['Tk']['window_title'])
    parent.resizable(False, False)
    parent.withdraw()
    
    print(parent.config())
    
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
    ttk.Button(startFrame, text="Exit", command=startTopLevel.destroy).grid(column=2, row=2, sticky=N)
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
    
    for i in range(0, 8):
        voteVar.append(StringVar())
        voteButton.append(ttk.Button(voteFrame, textvariable=voteVar[i], command=lambda index=i: removeContestant(index)))
        voteButton[i].grid(column=i % 4, row=math.ceil((1 + i) / 4), sticky=N)

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
    variables['gamemode'] = -1
    if mainTopLevel.config()['class'][4] == 'Tk':
        mainTopLevel.after(100, variableUpdates)
        
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
