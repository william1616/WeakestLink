from tkinter import *
from tkinter import ttk, filedialog, messagebox, simpledialog
import time, math, os.path

path = os.path.dirname(__file__)
try:
    import network, misc
except ImportError:
    import importlib.machinery
    loader = importlib.machinery.SourceFileLoader("network", os.path.join(path, "network.py"))
    network = loader.load_module("network")
    loader = importlib.machinery.SourceFileLoader("misc", os.path.join(path, "misc.py"))
    misc = loader.load_module("misc")

socket = network.initClientSocket()
running = False

def start():
    global address, socket, startFrame, waitFrame
    if network.attemptConnect(socket, address.get(), config['server']['bindPort']):
        startFrame.grid_forget()
        waitFrame.grid()
        isServerRunning()
    else:
        messagebox.showerror("Error", "Could not find server \"" + address.get() + "\"")

def isServerRunning():
    global socket, startTopLevel, mainTopLevel, running
    
    variables = network.getMessageofType('variables', [socket], False)
    if variables and variables['gamemode'] != -1: #if no longer listning for conections
        variableUpdates()
        startTopLevel.withdraw()
        mainTopLevel.deiconify()
        running = True
    else:
        if mainTopLevel.config()['class'][4] == 'Tk':
            mainTopLevel.after(100, isServerRunning)
        elif mainTopLevel.config()['class'][4] == 'Toplevel':
            mainTopLevel.root.after(100, isServerRunning)

def removeContestant(contestantIndex):
    global voteFrame, mainFrame, socket
    voteTopLevel.withdraw()
    mainTopLevel.deiconify()
    sendCommand(contestantIndex)
    
def sendCommand(cmd):
    global socket
    disableButton()
    network.sendMessage('cmd', cmd, socket)
    
def enableButton():
    global mainButton
    for key, value in mainButton.items():
        value.config(state='normal')
        
def disableButton():
    global mainButton
    for key, value in mainButton.items():
        value.config(state='disabled')
    
def initTk(parent):
    global address, question, status, cur_money, bank, voteVar, voteButton, config, startFrame, startTopLevel, mainTopLevel, voteTopLevel, waitFrame, mainButton, finalTopLevel, finalQuestion, finalStatus, finalName1, finalName2, finalScore1, finalScore2

    mainTopLevel = parent
    parent.title(config['Tk']['window_title'])
    parent.resizable(False, False)
    parent.withdraw()
    
    startTopLevel = Toplevel(parent)
    startTopLevel.title(config['Tk']['window_title'])
    startTopLevel.resizable(False, False)
    
    startMenu = Menu(startTopLevel)
    startTopLevel['menu'] = startMenu
    startFile = Menu(startMenu, tearoff=0)
    startTools = Menu(startMenu, tearoff=0)
    startHelp = Menu(startMenu, tearoff=0)
    startMenu.add_cascade(menu=startFile, label='File')
    startMenu.add_cascade(menu=startTools, label='Tools')
    startMenu.add_cascade(menu=startHelp, label='Help')
    
    startFile.add_command(label='Exit', command=close)
    
    startTools.add_command(label='What is my IP?', command=lambda: messagebox.showinfo("You IP Address is...", "\n".join(network.getIPAddress())))
    
    startHelp.add_command(label='About', command=lambda: messagebox.showinfo("About Weakest Link", "Remember to write some stuff here\nhttps://github.com/william1616/WeakestLink"))
    
    startFrame = ttk.Frame(startTopLevel, padding="3 3 3 3")
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
    
    mainButton = {}
    
    mainButton['correct'] = ttk.Button(mainFrame, text="Correct", command=lambda: sendCommand(1))
    mainButton['correct'].grid(column=2, row=1, sticky=N)
    mainButton['incorrect'] = ttk.Button(mainFrame, text="Incorrect", command=lambda: sendCommand(2))
    mainButton['incorrect'].grid(column=2, row=2, sticky=N)
    mainButton['bank'] = ttk.Button(mainFrame, text="Bank", command=lambda: sendCommand(3))
    mainButton['bank'].grid(column=3, row=2, sticky=N)
    mainButton['time'] = ttk.Button(mainFrame, text="Time Up", command=lambda: sendCommand(4))
    mainButton['time'].grid(column=3, row=1, sticky=N)
    
    mainMenu = Menu(mainTopLevel)
    mainTopLevel['menu'] = mainMenu
    mainFile = Menu(mainMenu, tearoff=0)
    mainTools = Menu(mainMenu, tearoff=0)
    mainHelp = Menu(mainMenu, tearoff=0)
    mainMenu.add_cascade(menu=mainFile, label='File')
    mainMenu.add_cascade(menu=mainTools, label='Tools')
    mainMenu.add_cascade(menu=mainHelp, label='Help')
    
    mainFile.add_command(label='Exit', command=close)
    
    mainTools.add_command(label='Goto Question...', command=gotoQuestion)
    
    mainHelp.add_command(label='About', command=lambda: messagebox.showinfo("About Weakest Link", "Remember to write some stuff here\nhttps://github.com/william1616/WeakestLink"))
    
    finalTopLevel = Toplevel(parent)
    finalTopLevel.title(config['Tk']['window_title'])
    finalTopLevel.resizable(False, False)
    finalTopLevel.withdraw()

    finalQuestion = StringVar()
    finalStatus = StringVar()
    finalName1 = StringVar()
    finalName2 = StringVar()
    finalScore1 = IntVar()
    finalScore2 = IntVar()

    ttk.Label(finalTopLevel, textvariable=finalStatus, width=100, background='red').grid(column=1, row=1, sticky=N)
    ttk.Label(finalTopLevel, textvariable=finalQuestion, width=100).grid(column=1, row=2, sticky=N)
    ttk.Label(finalTopLevel, textvariable=finalName1).grid(column=5, row=1, sticky=N)
    ttk.Label(finalTopLevel, textvariable=finalName2).grid(column=5, row=2, sticky=N)
    ttk.Label(finalTopLevel, textvariable=finalScore1).grid(column=6, row=1, sticky=N)
    ttk.Label(finalTopLevel, textvariable=finalScore2).grid(column=6, row=2, sticky=N)
    
    mainButton['finalCorrect'] = ttk.Button(finalTopLevel, text="Correct", command=lambda: sendCommand(1))
    mainButton['finalCorrect'].grid(column=2, row=1, sticky=N)
    mainButton['finalIncorrect'] = ttk.Button(finalTopLevel, text="Incorrect", command=lambda: sendCommand(2))
    mainButton['finalIncorrect'].grid(column=2, row=2, sticky=N)
    
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
        
    waitFrame = ttk.Frame(startTopLevel, padding="3 3 3 3")
    waitFrame.grid(column=0, row=0, sticky=(N, W, E, S))
    waitFrame.columnconfigure(0, weight=1)
    waitFrame.rowconfigure(0, weight=1)
    
    ttk.Label(waitFrame, text="Connected to Server").grid(column=0, row=0, sticky=N)
    ttk.Label(waitFrame, text="Waiting for Server to Start").grid(column=0, row=1, sticky=N)
    
    waitFrame.grid_remove()
    
    mainTopLevel.protocol("WM_DELETE_WINDOW", close)
    startTopLevel.protocol("WM_DELETE_WINDOW", close)
    voteTopLevel.protocol("WM_DELETE_WINDOW", close)

def gotoQuestion():
    global socket, running
    if running:
        questionNo = simpledialog.askinteger("Go to question...", "Question Number:")
        if questionNo:
            disableButton()
            network.sendMessage('gotoQu', questionNo, socket)
    else:
        messagebox.showerror("Error", "Server has not Started Running Yet!")
    
def selectMainQuestionFile():
    global config
    #this needs to be transmitted to server and validated
    config['questions']['mainQ'] = filedialog.askopenfilename()
    misc.writeConfig(config)
    
def selectFinalQuestionFile():
    global config
    #this needs to be transmitted to server and validated
    config['questions']['finalQ'] = filedialog.askopenfilename()
    misc.writeConfig(config)
    
def close():
    global mainTopLevel, startTopLevel, voteTopLevel
    startTopLevel.destroy()
    voteTopLevel.destroy()
    finalTopLevel.destroy()
    if mainTopLevel.config()['class'][4] == 'Toplevel': 
        mainTopLevel.root.deiconify()
    mainTopLevel.destroy()
    
def variableUpdates():
    global question, status, cur_money, bank, startTopLevel, mainTopLevel, voteTopLevel
    
    variables = network.getMessageofType('variables', [socket], False)
    #only do any processing if variables have been updated
    if variables:
        disableButton()
        if len(variables['contestants']) == 1:
            finalStatus.set(str(list(variables['contestants'])[0]) + ' is the winner!')
            finalQuestion.set('')
        elif variables['gamemode'] == 0:
            voteTopLevel.withdraw()
            if len(variables['contestants']) == 2:
                mainTopLevel.withdraw()
                finalStatus.set('Final Round starting')
                finalTopLevel.deiconify()
            else:
                status.set('Round ' + str(variables['cntRounds']) + ' starting')
                mainTopLevel.deiconify()
        elif variables['gamemode'] == 1:
            voteTopLevel.withdraw()
            status.set('Round ' + str(variables['cntRounds']) + ' Question ' + str(variables['cntRquestions']))
            question.set(list(variables['contestants'].keys())[variables['crtContestant']] + ': ' + variables['question'])
            cur_money.set(list(variables['money'])[variables['correct']])
            bank.set(variables['bank'])
            mainTopLevel.deiconify()
            enableButton()
        elif variables['gamemode'] == 2:
            mainTopLevel.withdraw()
            contestantList = list(variables['contestants'].keys())
            for i in range(0, 8):
                try:
                    voteVar[i].set(contestantList[i])
                except IndexError:
                    voteButton[i].grid_forget()
            voteTopLevel.deiconify()
        elif variables['gamemode'] == 4:
            voteTopLevel.withdraw()
            finalStatus.set('Final Question ' + str(variables['cntRquestions']))
            finalQuestion.set(list(variables['contestants'].keys())[variables['crtContestant']] + ': ' + variables['question'])
            if finalName1.get() == '':
                finalName1.set(list(variables['contestants'].keys())[0])
                finalName2.set(list(variables['contestants'].keys())[1])
            finalScore1.set(list(variables['contestants'].values())[0])
            finalScore2.set(list(variables['contestants'].values())[1])
            finalTopLevel.deiconify()
            enableButton()
        elif variables['gamemode'] == 5:
            finalStatus.set('Going to Head to Head Round')
            finalQuestion.set('')
    
    try:
        #run this function again in 100ms
        if mainTopLevel.config()['class'][4] == 'Tk':
            mainTopLevel.after(100, variableUpdates)
        elif mainTopLevel.config()['class'][4] == 'Toplevel':
            mainTopLevel.root.after(100, variableUpdates)
    except TclError:
        #dont call the function again
        pass

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
